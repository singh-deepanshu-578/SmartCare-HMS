/* =========================================
   SMART CARE HMS - MAIN JAVASCRIPT
   ========================================= */

/* =========================================
   PATIENT SESSION MANAGEMENT
========================================= */
function getPatientSession() {
  let sessionId = sessionStorage.getItem("patientSessionId");
  if (!sessionId) {
    sessionId = "PAT-" + Date.now() + "-" + Math.floor(Math.random() * 1000);
    sessionStorage.setItem("patientSessionId", sessionId);
  }
  return sessionId;
}

/* =========================================
   TRIAGE LOGIC (AI-SIMULATED)
========================================= */
function triage(symptom) {
  const triageMap = {
    'pain': { priority: "Critical", score: 1 },
    'trauma': { priority: "High", score: 2 },
    'burn': { priority: "High", score: 2 },
    'stroke': { priority: "Critical", score: 1 },
    'fever': { priority: "Medium", score: 3 },
    'weakness': { priority: "Medium", score: 3 },
    'routine': { priority: "Low", score: 4 }
  };
  
  return triageMap[symptom] || { priority: "Low", score: 4 };
}

/* =========================================
   FORM SUBMISSION HANDLERS
========================================= */
document.addEventListener("DOMContentLoaded", () => {
  
  // Emergency Booking Form
  const bookingForm = document.getElementById("bookingForm");
  if (bookingForm) {
    bookingForm.addEventListener("submit", function (e) {
      const statusBox = document.getElementById("helpStatus");
      const careModeEl = document.getElementById("careMode");
      
      if (statusBox && careModeEl) {
        const careMode = careModeEl.value;
        
        // Show feedback before form submits
        statusBox.classList.remove("d-none");
        
        if (careMode === "home") {
          statusBox.className = "alert alert-success mt-4";
          statusBox.innerHTML = "🚑 <strong>Help is on the way!</strong> A doctor has been assigned.";
        } else {
          statusBox.className = "alert alert-info mt-4";
          statusBox.innerHTML = "🏥 <strong>Hospital Assistance Confirmed</strong><br>Please proceed to the emergency ward.";
        }
      }
    });
  }
  
  // Feature Card Click Handlers
  document.querySelectorAll(".feature-card").forEach(card => {
    card.addEventListener("click", () => {
      const feature = card.dataset.feature;
      
      switch (feature) {
        case "home-care":
          window.location.href = "/home-care/";
          break;
          
        case "pre-alert":
          showAlert("Doctors are notified before patient arrival.");
          break;
          
        case "ai-severity":
          showAlert("AI automatically prioritizes emergency cases based on symptoms.");
          break;
          
        case "digital-token":
          showAlert("Each case gets a unique digital token for tracking.");
          break;
          
        case "family-dashboard":
          showAlert("Family can track treatment progress in real-time.");
          break;
          
        case "instructions":
          window.location.href = "/patient/#instructions";
          break;
      }
    });
  });
  
  // Initialize any dynamic content
  initDynamicContent();
});

/* =========================================
   UTILITY FUNCTIONS
========================================= */
function showAlert(message, type = 'info') {
  // Create alert element
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
  alertDiv.style.cssText = 'top: 80px; right: 20px; z-index: 9999; max-width: 400px;';
  alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  
  document.body.appendChild(alertDiv);
  
  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    alertDiv.remove();
  }, 5000);
}

function initDynamicContent() {
  // Add any initialization code here
  console.log('Smart Care HMS initialized');
}

/* =========================================
   API FUNCTIONS (For AJAX calls)
========================================= */
async function fetchEmergencyCases() {
  try {
    const response = await fetch('/api/emergency-cases/');
    const data = await response.json();
    return data.cases;
  } catch (error) {
    console.error('Error fetching emergency cases:', error);
    return [];
  }
}

async function fetchDoctorCases() {
  try {
    const response = await fetch('/api/doctor-cases/');
    const data = await response.json();
    return data.cases;
  } catch (error) {
    console.error('Error fetching doctor cases:', error);
    return [];
  }
}

async function fetchHospitals() {
  try {
    const response = await fetch('/api/hospitals/');
    const data = await response.json();
    return data.hospitals;
  } catch (error) {
    console.error('Error fetching hospitals:', error);
    return [];
  }
}

/* =========================================
   REAL-TIME UPDATES (WebSocket ready)
========================================= */
function initRealTimeUpdates() {
  // This can be extended with WebSocket for real-time updates
  // For now, using polling as fallback
  
  const updateInterval = setInterval(async () => {
    // Update emergency queue if on that page
    const queueTable = document.getElementById("queueTable");
    if (queueTable) {
      // Optionally refresh data via AJAX
      // const cases = await fetchEmergencyCases();
      // renderQueueTable(cases);
    }
  }, 30000); // Every 30 seconds
}

/* =========================================
   QUEUE RENDERING
========================================= */
function renderQueueTable(cases) {
  const table = document.getElementById("queueTable");
  if (!table) return;
  
  table.innerHTML = "";
  
  cases.forEach((p, index) => {
    const rowClass = p.priority === "Critical" ? "table-danger" : 
                     p.priority === "High" ? "table-warning" : 
                     p.priority === "Medium" ? "table-info" : "table-success";
    
    table.innerHTML += `
      <tr class="${rowClass}">
        <td>${index + 1}</td>
        <td>${p.token}</td>
        <td>${p.name}</td>
        <td>${p.symptom}</td>
        <td><strong>${p.priority}</strong></td>
        <td>${p.status}</td>
      </tr>
    `;
  });
}

/* =========================================
   DOCTOR DASHBOARD HELPERS
========================================= */
function updateCaseStatus(caseId, newStatus) {
  // This function can be used for AJAX status updates
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = `/doctor/case/${caseId}/update/`;
  
  const csrfInput = document.createElement('input');
  csrfInput.type = 'hidden';
  csrfInput.name = 'csrfmiddlewaretoken';
  csrfInput.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
  const statusInput = document.createElement('input');
  statusInput.type = 'hidden';
  statusInput.name = 'status';
  statusInput.value = newStatus;
  
  form.appendChild(csrfInput);
  form.appendChild(statusInput);
  document.body.appendChild(form);
  form.submit();
}

/* =========================================
   HOSPITAL SEARCH
========================================= */
function filterHospitals() {
  const value = document.getElementById("hospitalSearch").value.toLowerCase();
  document.querySelectorAll(".hospital-card").forEach(card => {
    card.style.display = card.innerText.toLowerCase().includes(value)
      ? "block" : "none";
  });
}

/* =========================================
   EMERGENCY INSTRUCTIONS
========================================= */
const emergencyInstructions = {
  pain: [
    "Make patient sit or lie comfortably",
    "Loosen tight clothing",
    "Do not give food or water",
    "Monitor breathing continuously"
  ],
  trauma: [
    "Do not move patient unnecessarily",
    "Apply pressure to stop bleeding",
    "Keep patient warm"
  ],
  burn: [
    "Cool burn with running water",
    "Do not apply ointments",
    "Cover with clean cloth"
  ],
  fever: [
    "Keep patient hydrated",
    "Monitor temperature",
    "Avoid heavy clothing"
  ],
  stroke: [
    "Note the time symptoms started",
    "Do not give food or drink",
    "Keep patient calm and lying down",
    "Clear airway if needed"
  ],
  weakness: [
    "Help patient sit or lie down",
    "Check for breathing",
    "Keep warm",
    "Stay with patient"
  ]
};

function showInstructions(symptom) {
  const list = document.getElementById("instructionList");
  if (!list || !emergencyInstructions[symptom]) return;
  
  list.innerHTML = "";
  emergencyInstructions[symptom].forEach(instruction => {
    list.innerHTML += `<li>${instruction}</li>`;
  });
}

// Initialize real-time updates on page load
document.addEventListener("DOMContentLoaded", initRealTimeUpdates);
