let map;
let userMarker;

async function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    center: { lat: 0, lng: 0 },
    zoom: 15
  });
}

document.getElementById('shareBtn').addEventListener('click', async () => {
  const btn = document.getElementById('shareBtn');
  const note = document.getElementById('note').value;
  
  btn.disabled = true;
  btn.textContent = 'Getting location...';
  
  if (!navigator.geolocation) {
    alert('Geolocation is not supported by your browser');
    btn.disabled = false;
    btn.textContent = 'Share My Location';
    return;
  }
  
  navigator.geolocation.getCurrentPosition(
    async (position) => {
      const { latitude, longitude } = position.coords;
      const accuracy = position.coords.accuracy;
      
      if (userMarker) userMarker.setMap(null);
      userMarker = new google.maps.Marker({
        position: { lat: latitude, lng: longitude },
        map: map,
        title: 'Your location'
      });
      
      map.setCenter({ lat: latitude, lng: longitude });
      document.getElementById('map').classList.remove('hidden');
      
      try {
        const res = await fetch('/api/locations', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ latitude, longitude, accuracy, note })
        });
        
        const data = await res.json();
        
        if (data.id) {
          const link = `${window.location.origin}${data.link}`;
          document.getElementById('shareLink').value = link;
          document.getElementById('result').classList.remove('hidden');
        }
      } catch (err) {
        alert('Failed to save location');
      }
      
      btn.disabled = false;
      btn.textContent = 'Share My Location';
    },
    (error) => {
      alert('Unable to get location: ' + error.message);
      btn.disabled = false;
      btn.textContent = 'Share My Location';
    }
  );
});

document.getElementById('copyBtn').addEventListener('click', () => {
  const input = document.getElementById('shareLink');
  input.select();
  document.execCommand('copy');
  document.getElementById('copyBtn').textContent = 'Copied!';
  setTimeout(() => {
    document.getElementById('copyBtn').textContent = 'Copy';
  }, 2000);
});