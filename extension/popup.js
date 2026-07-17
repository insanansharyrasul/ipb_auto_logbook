// Detect active tab and update action button dynamically if already on portal
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  const tab = tabs[0];
  if (tab && tab.url && tab.url.includes('studentportal.ipb.ac.id')) {
    const btn = document.getElementById('open-portal-btn');
    if (btn) {
      btn.style.background = '#10b981'; // Green color for success status
      btn.style.pointerEvents = 'none'; // Prevent navigation
      btn.innerHTML = '<span>✓ Anda sudah berada di Portal IPB</span>';
      
      // Append subtext guidance
      const container = btn.parentNode;
      const guideText = document.createElement('div');
      guideText.style.fontSize = '11px';
      guideText.style.color = '#059669';
      guideText.style.marginTop = '10px';
      guideText.style.fontWeight = '600';
      guideText.style.lineHeight = '1.4';
      guideText.textContent = 'Silakan gunakan panel kontrol melayang melalui ikon 📄 di pojok kanan bawah halaman portal Anda!';
      container.appendChild(guideText);
    }
  }
});
