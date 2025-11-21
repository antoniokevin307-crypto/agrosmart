(function () {
  // Config from template
  const cfg = window.WEATHER_MAP_CONFIG || {};
  const apiKey = cfg.apiKey || '';
  const center = cfg.center || [0, 0];
  const zoom = cfg.zoom || 6;
  const isSpecificCrop = cfg.is_specific_crop || false;

  if (!apiKey) {
    console.warn('No OpenWeatherMap API key provided (OPENWEATHERMAP_API_KEY). Map overlays disabled.');
  }

  // Wait until Leaflet is available
  function ready(cb) {
    const start = Date.now();
    const timeoutMs = 5000;
    (function poll() {
      if (typeof L !== 'undefined') return cb();
      if (Date.now() - start > timeoutMs) {
        console.warn('Leaflet (L) not available after', timeoutMs, 'ms. Map cannot initialize.');
        return;
      }
      setTimeout(poll, 50);
    })();
  }

  console.log('WEATHER_MAP_CONFIG (from template):', cfg);

  ready(function () {
    console.log('Leaflet available, initializing map...');
    try {
      const map = L.map('weather-map').setView(center, zoom);

      const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(map);

      // Overlay layers (require OpenWeatherMap API key)
      const overlays = {};

      if (apiKey) {
        // Capas meteorológicas con mayor contraste y color
        const temp = L.tileLayer(`https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=${apiKey}`, {
          maxZoom: 19,
          attribution: '&copy; OpenWeatherMap',
          opacity: 0.85, // Más visible
          zIndex: 500
        });

        const clouds = L.tileLayer(`https://tile.openweathermap.org/map/clouds_new/{z}/{x}/{y}.png?appid=${apiKey}`, {
          maxZoom: 19,
          attribution: '&copy; OpenWeatherMap',
          opacity: 0.75, // Más visible
          zIndex: 510
        });

        const precip = L.tileLayer(`https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=${apiKey}`, {
          maxZoom: 19,
          attribution: '&copy; OpenWeatherMap',
          opacity: 0.85, // Más visible
          zIndex: 520
        });

        overlays['🌡️ Temperatura (°C)'] = temp;
        overlays['☁️ Nubes'] = clouds;
        overlays['🌧️ Precipitación'] = precip;
      }

      // Control de capas
      L.control.layers({ 'OSM': osm }, overlays, { collapsed: false }).addTo(map);

      // Marcador del cultivo actual (cfg.current_crop)
      let currentCropMarker = null;
      if (cfg.current_crop && cfg.current_crop.lat && cfg.current_crop.lon) {
        const crop = cfg.current_crop;
        const descText = crop.description ? `<br><em>${crop.description}</em>` : '';
        const popupText = `<strong>${crop.name}</strong>${descText}<br>Lat: ${crop.lat.toFixed(4)}, Lon: ${crop.lon.toFixed(4)}`;
        currentCropMarker = L.marker([crop.lat, crop.lon]).addTo(map).bindPopup(popupText).openPopup();
      }

      // Función para actualizar el dashboard con datos de un cultivo
      function updateDashboardForCrop(cropId, lat, lon, name, description) {
        console.log('Fetching weather for crop', cropId);
        fetch(`/api/crop/${cropId}/weather/`)
          .then(response => response.json())
          .then(data => {
            if (data.ok) {
              // Actualizar tarjetas de clima
              document.querySelector('[data-weather="temperature"]').textContent = data.temperature + ' °C';
              document.querySelector('[data-weather="humidity"]').textContent = data.humidity + ' %';
              document.querySelector('[data-weather="rain"]').textContent = data.rain_mm + ' mm';
              document.querySelector('[data-weather="wind"]').textContent = data.wind_ms.toFixed(2) + ' m/s';
              
              // Actualizar recomendación
              const recElement = document.querySelector('[data-weather="recommendation"]');
              if (recElement) {
                recElement.textContent = data.recommendation;
              }
              
              // Actualizar título y ubicación
              document.querySelector('h2').textContent = `Dashboard ${data.crop_name}`;
              const locElement = document.querySelector('h2 + p small');
              if (locElement) {
                locElement.textContent = `Coordenadas: ${data.crop_lat || 'N/A'}, ${data.crop_lon || 'N/A'}`;
              }
              
              // Mover/crear marcador del cultivo actual y abrir popup con info completa
              const latVal = (data.crop_lat !== null && data.crop_lat !== undefined) ? parseFloat(data.crop_lat) : (lat || null);
              const lonVal = (data.crop_lon !== null && data.crop_lon !== undefined) ? parseFloat(data.crop_lon) : (lon || null);
              const popupDesc = data.crop_description ? `<br><em>${data.crop_description}</em>` : '';
              const popupContent = `<strong>${data.crop_name}</strong>${popupDesc}<br>Lat: ${latVal ? latVal.toFixed(4) : 'N/A'}, Lon: ${lonVal ? lonVal.toFixed(4) : 'N/A'}`;
              if (latVal && lonVal) {
                if (currentCropMarker) {
                  currentCropMarker.setLatLng([latVal, lonVal]).setPopupContent(popupContent).openPopup();
                } else {
                  currentCropMarker = L.marker([latVal, lonVal]).addTo(map).bindPopup(popupContent).openPopup();
                }
              }
              
              console.log('Dashboard updated for', data.crop_name);
            } else {
              console.error('Error fetching weather:', data.error);
            }
          })
          .catch(err => console.error('Fetch error:', err));
      }

      // Añadir marcadores para otros cultivos guardados (cfg.crops) con doble click listener
      if (Array.isArray(cfg.crops)) {
        cfg.crops.forEach(function (c) {
          try {
            if (c.lat && c.lon) {
              const descText = c.description ? `<br><em>${c.description}</em>` : '';
              const ownerText = c.owner_email ? `<br><small>Usuario: ${c.owner_email}</small>` : '';
              const popupText = `<strong>${c.name}</strong>${descText}${ownerText}<br>Lat: ${c.lat.toFixed(4)}, Lon: ${c.lon.toFixed(4)}`;
              
              // Determinar color del marcador
              let markerIcon = L.icon({
                iconUrl: `/static/img/marker-icon.png`, // Usar el mismo ícono para todos los marcadores
                shadowUrl: '/static/img/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41],
                className: c.is_owner ? 'marker-green' : 'marker-gray' // Clase CSS para diferenciar colores
              });
              
              const marker = L.marker([c.lat, c.lon], { icon: markerIcon }).addTo(map).bindPopup(popupText);
              
              // Doble click en marker para actualizar dashboard (solo si es del usuario actual o root)
              marker.on('dblclick', function () {
                if (c.is_owner) {
                  console.log('Double-clicked on crop', c.id);
                  // Centrar mapa en el cultivo
                  map.setView([c.lat, c.lon], 13);
                  // Actualizar datos del dashboard (pasar lat/lon para fallback)
                  updateDashboardForCrop(c.id, c.lat, c.lon, c.name, c.description);
                }
              });
            }
          } catch (e) {
            console.warn('Error adding crop marker', e, c);
          }
        });
      }

    } catch (err) {
      console.error('Error inicializando el mapa meteorológico:', err);
    }
  });
})();
