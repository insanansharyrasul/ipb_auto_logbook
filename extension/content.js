// IndexedDB File Storage Utilities
const DB_NAME = 'IPBLogbookCompanionDB';
const STORE_NAME = 'proof_files';

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, 1);
    request.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME);
      }
    };
    request.onsuccess = (e) => resolve(e.target.result);
    request.onerror = (e) => reject(e.target.error);
  });
}

async function saveFileToDB(name, file) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const req = store.put(file, name);
    req.onsuccess = () => resolve();
    req.onerror = () => reject(req.error);
  });
}

async function getFileFromDB(name) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const req = store.get(name);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function clearDB() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const req = store.clear();
    req.onsuccess = () => resolve();
    req.onerror = () => reject(req.error);
  });
}

// CSV Parsing is handled globally by PapaParse library

// Trigger CSV Template Download
function downloadCSVTemplate() {
  const headers = "tanggal,mulai,selesai,keterangan,file,tipe,lokasi,berita\n";
  const sampleRow = "16/07/2026,08:00,10:00,Revisi Laporan Kerja Harian,files/bukti.png,offline,Kantor Magang,kegiatan\n";
  
  const blob = new Blob([headers + sampleRow], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", "data_logbook_template.csv");
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Check current page type based on URL
function getPageType() {
  const url = window.location.href;
  if (url.includes('Account/Login')) {
    return 'login';
  } else if (url.includes('AktivitasKampusMerdeka')) {
    return 'aktivitas';
  } else if (url.includes('LogBookAktivitas') && !url.includes('Create') && !url.includes('Edit')) {
    return 'log_list';
  } else if (url.includes('LogBookAktivitas/Create') || url.includes('LogBookAktivitas/Edit') || document.querySelector('input[placeholder="Tanggal"]')) {
    return 'form';
  }
  return 'other';
}

// Injected UI Setup using Shadow DOM
let shadowRoot = null;
function injectUI() {
  // Prevent duplicate insertion
  if (document.getElementById('ipb-logbook-extension-root')) return;

  const container = document.createElement('div');
  container.id = 'ipb-logbook-extension-root';
  document.body.appendChild(container);
  
  shadowRoot = container.attachShadow({ mode: 'open' });
  
  const style = document.createElement('style');
  style.textContent = `
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600;700&display=swap');
    
    :host {
      font-family: 'Open Sans', 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
      font-size: 14px;
      color: #334155;
    }
    
    /* FAB (Floating Action Button) - IPB Blue Theme */
    .fab {
      position: fixed;
      bottom: 24px;
      right: 24px;
      width: 56px;
      height: 56px;
      border-radius: 28px;
      background: linear-gradient(135deg, #0056b3 0%, #003882 100%);
      box-shadow: 0 8px 30px rgba(0, 56, 130, 0.35);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      z-index: 99999;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .fab:hover {
      transform: scale(1.1) rotate(5deg);
      box-shadow: 0 12px 35px rgba(0, 56, 130, 0.5);
    }
    
    .fab svg {
      width: 24px;
      height: 24px;
      fill: none;
      stroke: #ffffff;
      stroke-width: 2;
      stroke-linecap: round;
      stroke-linejoin: round;
    }
    
    .fab.active-glow::after {
      content: '';
      position: absolute;
      width: 100%;
      height: 100%;
      border-radius: 50%;
      border: 2px solid #10b981;
      animation: pulse 1.8s infinite;
      box-shadow: 0 0 15px #10b981;
    }
    
    /* Main Panel Card - Clean White Theme */
    .panel {
      position: fixed;
      bottom: 96px;
      right: 24px;
      width: 390px;
      max-height: 585px;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.12);
      z-index: 99999;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
      transform-origin: bottom right;
      transform: scale(0);
      opacity: 0;
      pointer-events: none;
    }
    
    .panel.show {
      transform: scale(1);
      opacity: 1;
      pointer-events: auto;
    }
    
    /* Header - IPB Colors */
    .header {
      padding: 16px 20px;
      background: #f8fafc;
      border-bottom: 1px solid #e2e8f0;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    
    .title {
      font-weight: 700;
      font-size: 16px;
      color: #004c97;
      margin: 0;
    }
    
    .close-btn {
      background: transparent;
      border: none;
      color: #64748b;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 6px;
      border-radius: 50%;
      transition: all 0.2s;
    }
    
    .close-btn:hover {
      background: #e2e8f0;
      color: #0f172a;
    }
    
    /* Content Area */
    .content {
      padding: 20px;
      overflow-y: auto;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 14px;
      background: #ffffff;
    }
    
    .section-title {
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #004c97;
      font-weight: 700;
      margin-bottom: 4px;
      border-bottom: 1px solid #f1f5f9;
      padding-bottom: 4px;
    }
    
    .form-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    
    .form-group label {
      font-size: 12px;
      font-weight: 600;
      color: #475569;
    }
    
    input[type="text"], input[type="password"], input[type="file"] {
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 8px 12px;
      color: #0f172a;
      font-family: inherit;
      font-size: 13px;
      transition: all 0.2s;
    }
    
    input[type="text"]:focus, input[type="password"]:focus {
      outline: none;
      border-color: #004c97;
      background: #ffffff;
      box-shadow: 0 0 0 2px rgba(0, 76, 151, 0.15);
    }
    
    /* Custom File Input styling */
    .file-input-wrapper {
      position: relative;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    
    .file-btn {
      background: #f8fafc;
      border: 1px dashed #cbd5e1;
      border-radius: 8px;
      padding: 10px;
      text-align: center;
      cursor: pointer;
      font-size: 12px;
      color: #475569;
      transition: all 0.2s;
      font-weight: 500;
    }
    
    .file-btn:hover {
      background: rgba(0, 76, 151, 0.04);
      border-color: #004c97;
      color: #004c97;
    }
    
    /* Control Buttons */
    .btn-row {
      display: flex;
      gap: 8px;
      margin-top: 5px;
    }
    
    .btn {
      flex: 1;
      padding: 9px 14px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 13px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: all 0.2s;
      border: none;
      font-family: inherit;
    }
    
    .btn-primary {
      background: linear-gradient(135deg, #0056b3 0%, #003882 100%);
      color: #ffffff;
      box-shadow: 0 4px 12px rgba(0, 56, 130, 0.2);
    }
    
    .btn-primary:hover {
      background: linear-gradient(135deg, #003d80 0%, #00224d 100%);
      transform: translateY(-1px);
    }
    
    .btn-danger {
      background: rgba(239, 68, 68, 0.1);
      color: #ef4444;
      border: 1px solid rgba(239, 68, 68, 0.2);
    }
    
    .btn-danger:hover {
      background: rgba(239, 68, 68, 0.2);
    }
    
    .btn-secondary {
      background: #f1f5f9;
      color: #334155;
      border: 1px solid #e2e8f0;
    }
    
    .btn-secondary:hover {
      background: #e2e8f0;
    }
    
    .btn-link {
      background: rgba(232, 155, 0, 0.08);
      color: #b37700;
      border: 1px solid rgba(232, 155, 0, 0.2);
    }
    
    .btn-link:hover {
      background: rgba(232, 155, 0, 0.16);
    }
    
    .btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none !important;
      box-shadow: none !important;
    }
    
    /* Queue Preview list */
    .queue-container {
      max-height: 120px;
      overflow-y: auto;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      background: #f8fafc;
    }
    
    .queue-item {
      padding: 6px 10px;
      border-bottom: 1px solid #f1f5f9;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 11px;
      gap: 10px;
      color: #334155;
    }
    
    .queue-item:last-child {
      border-bottom: none;
    }
    
    .queue-item-info {
      flex: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .queue-item-date {
      color: #64748b;
      margin-right: 4px;
      font-weight: 600;
    }
    
    .status-badge {
      padding: 1px 5px;
      border-radius: 4px;
      font-size: 9px;
      font-weight: 700;
      text-transform: uppercase;
    }
    
    .status-pending { background: #e2e8f0; color: #475569; }
    .status-filling { background: rgba(0, 76, 151, 0.1); color: #004c97; }
    .status-success { background: #d1fae5; color: #065f46; }
    .status-failed { background: #fee2e2; color: #991b1b; }
    
    /* Status banner */
    .status-banner {
      background: rgba(0, 76, 151, 0.04);
      border: 1px solid rgba(0, 76, 151, 0.1);
      border-radius: 8px;
      padding: 8px 12px;
      font-size: 12px;
      line-height: 1.4;
      display: flex;
      align-items: center;
      gap: 10px;
      color: #334155;
    }
    
    .status-banner.running {
      background: #ecfdf5;
      border-color: rgba(16, 185, 129, 0.2);
      color: #065f46;
    }
    
    .pulse-dot {
      width: 8px;
      height: 8px;
      background-color: #004c97;
      border-radius: 50%;
    }
    
    .running .pulse-dot {
      background-color: #10b981;
      animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
      0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
      70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
      100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    
    .status-banner-text {
      flex: 1;
    }
    
    /* Small Footer */
    .footer {
      padding: 10px 20px;
      text-align: center;
      font-size: 11px;
      color: #64748b;
      border-top: 1px solid #e2e8f0;
      background: #f8fafc;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
      width: 6px;
    }
    ::-webkit-scrollbar-track {
      background: transparent;
    }
    ::-webkit-scrollbar-thumb {
      background: rgba(0, 0, 0, 0.1);
      border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: rgba(0, 0, 0, 0.2);
    }
  `;
  
  const fab = document.createElement('div');
  fab.className = 'fab';
  fab.innerHTML = `
    <svg viewBox="0 0 24 24">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
      <polyline points="14 2 14 8 20 8"></polyline>
      <line x1="16" y1="13" x2="8" y2="13"></line>
      <line x1="16" y1="17" x2="8" y2="17"></line>
      <polyline points="10 9 9 9 8 9"></polyline>
    </svg>
  `;
  
  const panel = document.createElement('div');
  panel.className = 'panel';
  panel.innerHTML = `
    <div class="header">
      <h3 class="title">IPB Logbook Companion</h3>
      <button class="close-btn" id="close-panel-btn">
        <svg style="width:16px;height:16px" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>
    
    <div class="content">
      <div class="status-banner" id="status-banner">
        <div class="pulse-dot"></div>
        <div class="status-banner-text" id="status-text">Siap melakukan otomasi. Unggah berkas CSV & berkas bukti untuk memulai.</div>
      </div>
      
      <!-- Account Credentials (matches GUI setup) -->
      <div class="form-group">
        <div class="section-title">Kredensial Akun</div>
        <div class="btn-row">
          <div class="form-group" style="flex:1">
            <label for="username-input">Nama Pengguna</label>
            <input type="text" id="username-input" placeholder="NRP / ID Pengguna" />
          </div>
          <div class="form-group" style="flex:1">
            <label for="password-input">Kata Sandi</label>
            <input type="password" id="password-input" placeholder="••••••••" />
          </div>
        </div>
      </div>
      
      <div class="form-group">
        <div class="section-title">Parameter Logbook</div>
        <label for="dosen-input">Dosen Penggerak</label>
        <input type="text" id="dosen-input" placeholder="Jeffrey Einstein, S.Komp., Ph.D." />
      </div>
      
      <div class="btn-row">
        <div class="form-group" style="flex:1">
          <label for="row-input">Nomor Baris</label>
          <input type="text" id="row-input" placeholder="1" />
        </div>
        <div class="form-group" style="flex:2">
          <label for="semester-input">Semester</label>
          <input type="text" id="semester-input" placeholder="2026/2027 Semester Genap" />
        </div>
      </div>
      
      <div class="form-group">
        <div class="section-title">Sumber Data & Templat</div>
        
        <div class="btn-row">
          <button class="btn btn-link" id="template-btn" style="flex:1">⬇ Unduh Template CSV</button>
        </div>
        
        <div class="file-input-wrapper">
          <div class="file-btn" id="csv-btn">📁 Unggah data.csv</div>
          <input type="file" id="csv-file" accept=".csv" style="display:none" />
        </div>
        
        <div class="file-input-wrapper">
          <div class="file-btn" id="proof-btn">🖼 Pilih Berkas Bukti</div>
          <input type="file" id="proof-files" multiple accept="image/*,application/pdf" style="display:none" />
        </div>
        <div id="file-count" style="font-size:11px;color:#64748b;margin-top:-4px">0 berkas bukti tersimpan di memori</div>
      </div>
      
      <div class="form-group" id="queue-section" style="display:none">
        <div class="section-title" id="queue-title">Antrean Logbook (0 baris)</div>
        <div class="queue-container" id="queue-list"></div>
      </div>
      
      <div class="btn-row">
        <button class="btn btn-primary" id="start-btn" disabled>▶ Mulai Pengisian</button>
        <button class="btn btn-secondary" id="reset-btn">Atur Ulang</button>
      </div>
    </div>
    
    <div class="footer">
      IPB Auto Logbook Companion v1.0.0
    </div>
  `;
  
  shadowRoot.appendChild(style);
  shadowRoot.appendChild(fab);
  shadowRoot.appendChild(panel);
  
  // Wire up UI toggles
  fab.addEventListener('click', () => {
    panel.classList.toggle('show');
  });
  
  shadowRoot.getElementById('close-panel-btn').addEventListener('click', () => {
    panel.classList.remove('show');
  });
  
  // Bind input elements, buttons and file pickers
  const csvBtn = shadowRoot.getElementById('csv-btn');
  const csvFileInput = shadowRoot.getElementById('csv-file');
  const proofBtn = shadowRoot.getElementById('proof-btn');
  const proofFilesInput = shadowRoot.getElementById('proof-files');
  const startBtn = shadowRoot.getElementById('start-btn');
  const resetBtn = shadowRoot.getElementById('reset-btn');
  const templateBtn = shadowRoot.getElementById('template-btn');
  
  const usernameInput = shadowRoot.getElementById('username-input');
  const passwordInput = shadowRoot.getElementById('password-input');
  const dosenInput = shadowRoot.getElementById('dosen-input');
  const rowInput = shadowRoot.getElementById('row-input');
  const semesterInput = shadowRoot.getElementById('semester-input');
  
  csvBtn.addEventListener('click', () => csvFileInput.click());
  proofBtn.addEventListener('click', () => proofFilesInput.click());
  templateBtn.addEventListener('click', downloadCSVTemplate);
  
  // Storage sync on inputs
  usernameInput.addEventListener('input', (e) => {
    chrome.storage.local.set({ username: e.target.value });
  });
  passwordInput.addEventListener('input', (e) => {
    chrome.storage.local.set({ password: e.target.value });
  });
  dosenInput.addEventListener('input', (e) => {
    chrome.storage.local.set({ dosen: e.target.value });
    checkReadyState();
  });
  rowInput.addEventListener('input', (e) => {
    chrome.storage.local.set({ rowNumber: e.target.value });
  });
  semesterInput.addEventListener('input', (e) => {
    chrome.storage.local.set({ semester: e.target.value });
  });
  
  // CSV file picker change event
  csvFileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(evt) {
      try {
        const results = Papa.parse(evt.target.result, {
          header: true,
          skipEmptyLines: 'greedy',
          transformHeader: h => h.trim().toLowerCase()
        });
        const parsed = results.data;
        if (parsed.length === 0) {
          alert('Berkas CSV kosong atau tidak valid.');
          return;
        }
        chrome.storage.local.set({ 
          queue: parsed,
          currentIndex: 0,
          csvFileName: file.name
        }, () => {
          csvBtn.textContent = `📄 CSV: ${file.name}`;
          csvBtn.style.borderColor = '#3b82f6';
          csvBtn.style.color = '#3b82f6';
          renderQueue(parsed, 0);
          checkReadyState();
        });
      } catch (err) {
        alert('Gagal mengurai CSV: ' + err.message);
      }
    };
    reader.readAsText(file);
  });
  
  // Proof files picker change event
  proofFilesInput.addEventListener('change', async (e) => {
    const files = e.target.files;
    if (files.length === 0) return;
    
    let successCount = 0;
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      try {
        await saveFileToDB(file.name, file);
        successCount++;
      } catch (err) {
        console.error(`Gagal menyimpan berkas ${file.name}:`, err);
      }
    }
    
    shadowRoot.getElementById('file-count').textContent = `${successCount} berkas bukti tersimpan di memori peramban`;
    proofBtn.textContent = `🖼 Berhasil Memuat ${successCount} Berkas`;
    proofBtn.style.borderColor = '#10b981';
    proofBtn.style.color = '#10b981';
  });
  
  // Start Button Event
  startBtn.addEventListener('click', () => {
    chrome.storage.local.get(['automatorActive'], (res) => {
      if (res.automatorActive) {
        // Stop Automation
        chrome.storage.local.set({ automatorActive: false }, () => {
          setAutomatingUI(false);
          updateStatusText('Otomasi dijeda.');
        });
      } else {
        // Start Automation
        chrome.storage.local.set({ automatorActive: true }, () => {
          setAutomatingUI(true);
          updateStatusText('Otomasi dimulai. Mengalihkan/mengisi formulir...');
          runAutomationStep();
        });
      }
    });
  });
  
  // Reset Button Event
  resetBtn.addEventListener('click', () => {
    if (confirm('Apakah Anda yakin ingin mengatur ulang semua konfigurasi dan berkas yang telah dimuat?')) {
      chrome.storage.local.clear(() => {
        clearDB().then(() => {
          // Reset UI elements
          usernameInput.value = '';
          passwordInput.value = '';
          dosenInput.value = '';
          rowInput.value = '';
          semesterInput.value = '';
          csvBtn.textContent = '📁 Unggah data.csv';
          csvBtn.style.borderColor = '';
          csvBtn.style.color = '';
          proofBtn.textContent = '🖼 Pilih Berkas Bukti';
          proofBtn.style.borderColor = '';
          proofBtn.style.color = '';
          shadowRoot.getElementById('file-count').textContent = '0 berkas bukti tersimpan di memori';
          shadowRoot.getElementById('queue-section').style.display = 'none';
          startBtn.disabled = true;
          startBtn.textContent = '▶ Mulai Pengisian';
          setAutomatingUI(false);
          updateStatusText('Siap melakukan otomasi. Unggah berkas CSV & berkas bukti untuk memulai.');
        });
      });
    }
  });
  
  // Restore State on Load
  chrome.storage.local.get([
    'username', 'password', 'dosen', 'rowNumber', 'semester', 'queue', 'currentIndex', 'automatorActive', 'csvFileName'
  ], (res) => {
    if (res.username) usernameInput.value = res.username;
    if (res.password) passwordInput.value = res.password;
    if (res.dosen) dosenInput.value = res.dosen;
    if (res.rowNumber) rowInput.value = res.rowNumber;
    if (res.semester) semesterInput.value = res.semester;
    if (res.csvFileName) {
      csvBtn.textContent = `📄 CSV: ${res.csvFileName}`;
      csvBtn.style.borderColor = '#3b82f6';
      csvBtn.style.color = '#3b82f6';
    }
    if (res.queue) {
      renderQueue(res.queue, res.currentIndex || 0);
    }
    
    // Check IndexedDB file count to display
    openDB().then((db) => {
      const tx = db.transaction(STORE_NAME, 'readonly');
      const store = tx.objectStore(STORE_NAME);
      const req = store.getAllKeys();
      req.onsuccess = () => {
        const count = req.result.length;
        if (count > 0) {
          shadowRoot.getElementById('file-count').textContent = `${count} berkas bukti tersimpan di memori peramban`;
          proofBtn.textContent = `🖼 Berhasil Memuat ${count} Berkas`;
          proofBtn.style.borderColor = '#10b981';
          proofBtn.style.color = '#10b981';
        }
      };
    });
    
    checkReadyState();
    
    if (res.automatorActive) {
      setAutomatingUI(true);
      panel.classList.add('show');
      runAutomationStep();
    }
  });
}

function checkReadyState() {
  const dosen = shadowRoot.getElementById('dosen-input').value.trim();
  const startBtn = shadowRoot.getElementById('start-btn');
  
  chrome.storage.local.get(['queue'], (res) => {
    if (dosen && res.queue && res.queue.length > 0) {
      startBtn.disabled = false;
    } else {
      startBtn.disabled = true;
    }
  });
}

function setAutomatingUI(active) {
  const startBtn = shadowRoot.getElementById('start-btn');
  const banner = shadowRoot.getElementById('status-banner');
  const fab = shadowRoot.querySelector('.fab');
  
  if (active) {
    startBtn.textContent = '⏸ Jeda Pengisian';
    startBtn.classList.remove('btn-primary');
    startBtn.classList.add('btn-danger');
    banner.classList.add('running');
    fab.classList.add('active-glow');
  } else {
    startBtn.textContent = '▶ Mulai Pengisian';
    startBtn.classList.remove('btn-danger');
    startBtn.classList.add('btn-primary');
    banner.classList.remove('running');
    fab.classList.remove('active-glow');
  }
}

function updateStatusText(text) {
  const statusText = shadowRoot.getElementById('status-text');
  if (statusText) {
    statusText.textContent = text;
  }
}

function renderQueue(queue, currentIndex) {
  const container = shadowRoot.getElementById('queue-list');
  const section = shadowRoot.getElementById('queue-section');
  const title = shadowRoot.getElementById('queue-title');
  
  if (!queue || queue.length === 0) {
    section.style.display = 'none';
    return;
  }
  
  section.style.display = 'block';
  title.textContent = `Antrean Logbook (${queue.length} baris)`;
  container.innerHTML = '';
  
  queue.forEach((row, i) => {
    const item = document.createElement('div');
    item.className = 'queue-item';
    
    let statusClass = 'status-pending';
    let statusLabel = 'Menunggu';
    
    if (i < currentIndex) {
      statusClass = 'status-success';
      statusLabel = 'Selesai';
    } else if (i === currentIndex) {
      statusClass = 'status-filling';
      statusLabel = 'Sedang Diisi';
    }
    
    item.innerHTML = `
      <span class="queue-item-info">
        <span class="queue-item-date">${row.tanggal}</span>
        <span>${row.keterangan || 'Tanpa Keterangan'}</span>
      </span>
      <span class="status-badge ${statusClass}">${statusLabel}</span>
    `;
    container.appendChild(item);
  });
}

// core automation steps matching Python's Playwright code
async function runAutomationStep() {
  chrome.storage.local.get(['automatorActive', 'queue', 'currentIndex', 'dosen', 'rowNumber', 'semester', 'username', 'password'], async (res) => {
    if (!res.automatorActive || !res.queue || res.currentIndex === undefined) return;
    
    const queue = res.queue;
    const idx = res.currentIndex;
    const dosenName = res.dosen;
    
    if (idx >= queue.length) {
      // Completed!
      chrome.storage.local.set({ automatorActive: false }, () => {
        setAutomatingUI(false);
        updateStatusText('🎉 Berhasil! Semua entri telah terkirim.');
        if (shadowRoot) {
          renderQueue(queue, idx);
        }
      });
      return;
    }
    
    const pageType = getPageType();
    const row = queue[idx];
    
    if (pageType === 'login') {
      updateStatusText('Melakukan masuk log otomatis ke Portal...');
      
      const uInput = document.querySelector('input[placeholder="Username"]');
      const pInput = document.querySelector('input[placeholder="Password"]');
      const lBtn = Array.from(document.querySelectorAll('button, input[type="submit"]')).find(el => el.textContent.trim() === 'Masuk' || el.value === 'Masuk');
      
      if (uInput && pInput && lBtn && res.username && res.password) {
        uInput.value = res.username;
        uInput.dispatchEvent(new Event('input', { bubbles: true }));
        uInput.dispatchEvent(new Event('change', { bubbles: true }));
        
        pInput.value = res.password;
        pInput.dispatchEvent(new Event('input', { bubbles: true }));
        pInput.dispatchEvent(new Event('change', { bubbles: true }));
        
        await new Promise(r => setTimeout(r, 800));
        lBtn.click();
      } else {
        updateStatusText('⚠️ Tidak dapat masuk log otomatis. Silakan isi kredensial di panel ekstensi terlebih dahulu.');
        chrome.storage.local.set({ automatorActive: false }, () => setAutomatingUI(false));
      }
      
    } else if (pageType === 'aktivitas') {
      updateStatusText(`[${idx+1}/${queue.length}] Mencari baris nomor ${res.rowNumber} untuk semester ${res.semester}...`);
      
      const rows = Array.from(document.querySelectorAll('table tbody tr'));
      const targetRow = rows.find(r => {
        const text = r.textContent || '';
        return text.includes(res.rowNumber) && text.includes(res.semester);
      });
      
      if (targetRow) {
        const links = targetRow.querySelectorAll('a');
        if (links.length >= 3) {
          updateStatusText(`[${idx+1}/${queue.length}] Membuka halaman daftar logbook...`);
          links[2].click();
        } else {
          updateStatusText('❌ Baris ditemukan, tetapi tautan logbook tidak ditemukan.');
          chrome.storage.local.set({ automatorActive: false }, () => setAutomatingUI(false));
        }
      } else {
        updateStatusText(`❌ Baris No: "${res.rowNumber}" & Semester: "${res.semester}" tidak ditemukan.`);
        chrome.storage.local.set({ automatorActive: false }, () => setAutomatingUI(false));
      }
      
    } else if (pageType === 'log_list') {
      updateStatusText(`[${idx+1}/${queue.length}] Membuka formulir pengisian (menekan 'Tambah')...`);
      
      const tambahBtn = Array.from(document.querySelectorAll('a, button')).find(el => el.textContent.trim() === 'Tambah');
      if (tambahBtn) {
        tambahBtn.click();
      } else {
        updateStatusText('❌ Gagal menemukan tombol "Tambah" di halaman logbook.');
        chrome.storage.local.set({ automatorActive: false }, () => setAutomatingUI(false));
      }
      
    } else if (pageType === 'form') {
      updateStatusText(`[${idx+1}/${queue.length}] Mengisi: ${row.keterangan || 'Entri Kegiatan'}...`);
      
      try {
        // 1. Tanggal
        const tglInput = document.querySelector('input[placeholder="Tanggal"]');
        if (tglInput) {
          tglInput.value = row.tanggal;
          tglInput.dispatchEvent(new Event('input', { bubbles: true }));
          tglInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
        
        // 2. Waktu Selesai
        const selesaiInput = document.querySelector('input[placeholder="Waktu Selesai"]');
        if (selesaiInput) {
          selesaiInput.value = row.selesai;
          selesaiInput.dispatchEvent(new Event('input', { bubbles: true }));
          selesaiInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
        
        // 3. Waktu Mulai
        const mulaiInput = document.querySelector('input[placeholder="Waktu Mulai"]');
        if (mulaiInput) {
          mulaiInput.value = row.mulai;
          mulaiInput.dispatchEvent(new Event('input', { bubbles: true }));
          mulaiInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
        
        // 4. Berita Acara (Custom Select Dropdown)
        let selectTrigger = document.querySelector('[role="textbox"]') || 
                            Array.from(document.querySelectorAll('.select2-selection, .ant-select-selector, .form-control')).find(el => el.textContent.includes('-- Pilih --'));
        
        if (selectTrigger) {
          selectTrigger.click();
          await new Promise(r => setTimeout(r, 400));
          
          let optionText = '';
          const beritaClean = row.berita.toLowerCase().replace(/ /g, '');
          if (beritaClean === 'kegiatan') {
            optionText = 'Berita Acara Kegiatan';
          } else if (beritaClean === 'ujian') {
            optionText = 'Berita Acara Ujian';
          } else if (beritaClean === 'bimbingan') {
            optionText = 'Berita Acara Pembimbingan';
          }
          
          if (optionText) {
            const options = Array.from(document.querySelectorAll('[role="option"], .select2-results__option, option'));
            const targetOption = options.find(opt => opt.textContent.includes(optionText));
            if (targetOption) {
              if (targetOption.tagName === 'OPTION') {
                targetOption.selected = true;
                targetOption.parentElement.dispatchEvent(new Event('change', { bubbles: true }));
              } else {
                targetOption.click();
              }
            } else {
              // Fallback
              const anyOption = Array.from(document.querySelectorAll('*')).find(el => el.textContent.includes(optionText) && el.offsetParent !== null);
              if (anyOption) anyOption.click();
            }
          }
        }
        
        // 5. Dosen Penggerak
        const labels = Array.from(document.querySelectorAll('label'));
        const targetLabel = labels.find(l => l.textContent.toLowerCase().includes(dosenName.toLowerCase()));
        if (targetLabel) {
          const inputId = targetLabel.getAttribute('for');
          const input = inputId ? document.getElementById(inputId) : targetLabel.querySelector('input[type="checkbox"]');
          if (input) {
            input.checked = true;
            input.dispatchEvent(new Event('change', { bubbles: true }));
          } else {
            targetLabel.click();
          }
        }
        
        // 6. Tipe
        const typeClean = row.tipe.toLowerCase().replace(/ /g, '');
        let typeLabelText = '';
        if (typeClean === 'offline') typeLabelText = 'Offline';
        else if (typeClean === 'online') typeLabelText = 'Online';
        else if (typeClean === 'hybrid') typeLabelText = 'Hybrid';
        
        if (typeLabelText) {
          const typeLabel = labels.find(l => l.textContent.trim() === typeLabelText);
          if (typeLabel) {
            const inputId = typeLabel.getAttribute('for');
            const input = inputId ? document.getElementById(inputId) : typeLabel.querySelector('input[type="radio"], input[type="checkbox"]');
            if (input) {
              input.checked = true;
              input.dispatchEvent(new Event('change', { bubbles: true }));
            } else {
              typeLabel.click();
            }
          }
        }
        
        // 7. Lokasi
        const lokasiInput = document.querySelector('input[placeholder="Lokasi"]');
        if (lokasiInput) {
          lokasiInput.value = row.lokasi;
          lokasiInput.dispatchEvent(new Event('input', { bubbles: true }));
          lokasiInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
        
        // 8. Topik (Keterangan)
        const topikInput = document.querySelector('input[placeholder="Topik"]') || document.querySelector('textarea[placeholder="Topik"]');
        if (topikInput) {
          topikInput.value = row.keterangan;
          topikInput.dispatchEvent(new Event('input', { bubbles: true }));
          topikInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
        
        // 9. File Upload (Programmatic setting using DataTransfer from IndexedDB)
        const fileInput = document.querySelector('#File');
        if (fileInput && row.file) {
          const filename = row.file.split('/').pop();
          const fileObj = await getFileFromDB(filename);
          if (fileObj) {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(fileObj);
            fileInput.files = dataTransfer.files;
            fileInput.dispatchEvent(new Event('change', { bubbles: true }));
            updateStatusText(`[${idx+1}/${queue.length}] Formulir terisi. Mengunggah: ${filename}`);
          } else {
            console.warn(`Berkas ${filename} tidak ditemukan di memori peramban IndexedDB.`);
            updateStatusText(`[${idx+1}/${queue.length}] Formulir terisi. Berkas bukti tidak ditemukan di memori!`);
          }
        }
        
        // Wait 1.5 seconds for visual confirmation and inputs to process
        await new Promise(r => setTimeout(r, 1500));
        
        // Click Simpan (Submit Form)
        const simpanBtn = Array.from(document.querySelectorAll('button, input[type="submit"]')).find(el => el.textContent.trim() === 'Simpan' || el.value === 'Simpan');
        if (simpanBtn) {
          chrome.storage.local.set({ currentIndex: idx + 1 }, () => {
            simpanBtn.click();
          });
        } else {
          updateStatusText('❌ Gagal menemukan tombol "Simpan".');
          chrome.storage.local.set({ automatorActive: false }, () => setAutomatingUI(false));
        }
        
      } catch (err) {
        console.error('Gagal mengisi baris data:', err);
        updateStatusText(`❌ Gagal mengisi baris data: ${err.message}`);
        chrome.storage.local.set({ automatorActive: false }, () => setAutomatingUI(false));
      }
      
    } else {
      updateStatusText('Silakan buka halaman Aktivitas MBKM atau Logbook Portal Mahasiswa IPB untuk memulai otomasi.');
      chrome.storage.local.set({ automatorActive: false }, () => setAutomatingUI(false));
    }
  });
}

// Initialize on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', injectUI);
} else {
  injectUI();
}
