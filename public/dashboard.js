async function loadLocations() {
  try {
    const res = await fetch('/api/locations');
    const locations = await res.json();
    
    const tbody = document.getElementById('locationsBody');
    const emptyMsg = document.getElementById('emptyMsg');
    const table = document.getElementById('locationsTable');
    
    if (locations.length === 0) {
      table.classList.add('hidden');
      emptyMsg.classList.remove('hidden');
      return;
    }
    
    table.classList.remove('hidden');
    emptyMsg.classList.add('hidden');
    
    tbody.innerHTML = locations.map(loc => `
      <tr>
        <td><a href="/view.html?id=${loc.id}">${loc.id}</a></td>
        <td>${loc.note || '-'}</td>
        <td>${new Date(loc.created_at).toLocaleString()}</td>
        <td>
          <button class="btn-danger" onclick="deleteLocation('${loc.id}')">Delete</button>
        </td>
      </tr>
    `).join('');
    
  } catch (err) {
    console.error('Failed to load locations:', err);
  }
}

async function deleteLocation(id) {
  if (!confirm('Delete this location link?')) return;
  
  try {
    const res = await fetch(`/api/locations/${id}`, { method: 'DELETE' });
    
    if (res.ok) {
      loadLocations();
    } else {
      alert('Failed to delete location');
    }
  } catch (err) {
    alert('Failed to delete location');
  }
}

loadLocations();