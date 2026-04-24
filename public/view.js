let map;
let marker;

async function initViewMap() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get('id');
  
  if (!id) {
    document.getElementById('info').innerHTML = '<p class="empty">No location ID provided</p>';
    return;
  }
  
  try {
    const res = await fetch(`/api/locations/${id}`);
    
    if (!res.ok) {
      document.getElementById('info').innerHTML = '<p class="empty">Location not found</p>';
      return;
    }
    
    const loc = await res.json();
    
    document.getElementById('lat').textContent = loc.latitude.toFixed(6);
    document.getElementById('lng').textContent = loc.longitude.toFixed(6);
    document.getElementById('acc').textContent = loc.accuracy ? loc.accuracy.toFixed(0) : 'N/A';
    document.getElementById('time').textContent = new Date(loc.created_at).toLocaleString();
    document.getElementById('note').textContent = loc.note || 'No note';
    
    map = new google.maps.Map(document.getElementById('map'), {
      center: { lat: loc.latitude, lng: loc.longitude },
      zoom: 16
    });
    
    marker = new google.maps.Marker({
      position: { lat: loc.latitude, lng: loc.longitude },
      map: map,
      title: loc.note || 'Shared location'
    });
    
  } catch (err) {
    document.getElementById('info').innerHTML = '<p class="empty">Failed to load location</p>';
  }
}