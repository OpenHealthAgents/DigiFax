import React, { useState, useEffect, useRef } from "react";

// Types representing structured clinical variables
interface ExtractedValue {
  value: string;
  evidence: string;
  confidence: number;
}

interface ObservationRow {
  id: string;
  analyte_name: ExtractedValue;
  value: ExtractedValue;
  unit: ExtractedValue;
  reference_range: ExtractedValue;
}

interface AuditLog {
  timestamp: string;
  message: string;
}

function App() {
  // Document level state
  const [documentId] = useState("doc-99824-A");
  const [documentType, setDocumentType] = useState<ExtractedValue>({
    value: "LABORATORY REPORT",
    evidence: "CLINICAL PATHOLOGY LABORATORY REPORT",
    confidence: 0.98,
  });

  // Patient details state
  const [patientName, setPatientName] = useState<ExtractedValue>({
    value: "John Doe",
    evidence: "Patient Name: John Doe",
    confidence: 0.99,
  });
  const [patientDob, setPatientDob] = useState<ExtractedValue>({
    value: "1990-01-01",
    evidence: "DOB: 01/01/1990",
    confidence: 0.95,
  });
  const [patientGender, setPatientGender] = useState<ExtractedValue>({
    value: "Male",
    evidence: "Sex: M",
    confidence: 0.88,
  });
  const [patientMrn, setPatientMrn] = useState<ExtractedValue>({
    value: "MRN-12345",
    evidence: "MRN: 12345",
    confidence: 0.65, // low confidence to visualize alert styling!
  });

  // Observations state
  const [observations, setObservations] = useState<ObservationRow[]>([
    {
      id: "obs-1",
      analyte_name: { value: "Glucose", evidence: "Fasting Glucose", confidence: 0.99 },
      value: { value: "145", evidence: "145 mg/dL", confidence: 0.98 },
      unit: { value: "mg/dL", evidence: "mg/dL", confidence: 0.95 },
      reference_range: { value: "70-100", evidence: "Normal: 70 - 100 mg/dL", confidence: 0.92 },
    },
    {
      id: "obs-2",
      analyte_name: { value: "Cholesterol", evidence: "Total Cholesterol", confidence: 0.97 },
      value: { value: "240", evidence: "240 mg/dL", confidence: 0.96 },
      unit: { value: "mg/dL", evidence: "mg/dL", confidence: 0.95 },
      reference_range: { value: "<200", evidence: "Desirable: <200", confidence: 0.89 },
    },
  ]);

  // Selected active field to coordinate PDF highlighting
  const [selectedField, setSelectedField] = useState<string>("documentType");
  const [status, setStatus] = useState<"pending" | "approved" | "rejected">("pending");
  const [auditTrail, setAuditTrail] = useState<AuditLog[]>([
    { timestamp: "22:55:00", message: "Document uploaded and ingested successfully." },
    { timestamp: "22:55:02", message: "AI extraction executed using Gemini-1.5-Flash." },
  ]);

  // Form field focus tracker to update selected PDF bounding box
  const pdfContainerRef = useRef<HTMLDivElement>(null);

  // Coordinate coordinates for overlays relative to A4 page dimensions
  const boundingBoxes: Record<string, { left: string; top: string; width: string; height: string }> = {
    documentType: { left: "12%", top: "7%", width: "76%", height: "4.5%" },
    "patient.name": { left: "28%", top: "18%", width: "24%", height: "3.2%" },
    "patient.dob": { left: "28%", top: "22.5%", width: "18%", height: "3.2%" },
    "patient.gender": { left: "68%", top: "18%", width: "12%", height: "3.2%" },
    "patient.mrn": { left: "68%", top: "22.5%", width: "15%", height: "3.2%" },
    // Obs 1
    "observations.0.analyte_name": { left: "10%", top: "37.5%", width: "22%", height: "3.5%" },
    "observations.0.value": { left: "37%", top: "37.5%", width: "10%", height: "3.5%" },
    "observations.0.unit": { left: "52%", top: "37.5%", width: "10%", height: "3.5%" },
    "observations.0.reference_range": { left: "67%", top: "37.5%", width: "23%", height: "3.5%" },
    // Obs 2
    "observations.1.analyte_name": { left: "10%", top: "42.5%", width: "22%", height: "3.5%" },
    "observations.1.value": { left: "37%", top: "42.5%", width: "10%", height: "3.5%" },
    "observations.1.unit": { left: "52%", top: "42.5%", width: "10%", height: "3.5%" },
    "observations.1.reference_range": { left: "67%", top: "42.5%", width: "23%", height: "3.5%" },
  };

  // Keyboard shortcut actions
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl + Enter to Approve
      if (e.ctrlKey && e.key === "Enter") {
        e.preventDefault();
        handleApprove();
      }
      // Ctrl + Backspace to Reject
      if (e.ctrlKey && e.key === "Backspace") {
        e.preventDefault();
        handleReject();
      }
      // Ctrl + S to Save
      if (e.ctrlKey && e.key === "s") {
        e.preventDefault();
        handleSave();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [patientName, patientDob, patientGender, patientMrn, observations, documentType]);

  const logAudit = (message: string) => {
    const timeStr = new Date().toTimeString().split(" ")[0];
    setAuditTrail((prev) => [...prev, { timestamp: timeStr, message }]);
  };

  const handleApprove = () => {
    setStatus("approved");
    logAudit("Report APPROVED by reviewer.");
    alert("Report successfully approved and compiled to FHIR R4 Bundle!");
  };

  const handleReject = () => {
    setStatus("rejected");
    logAudit("Report REJECTED by reviewer.");
    alert("Report rejected. Status updated.");
  };

  const handleSave = () => {
    logAudit("Saved manual corrections successfully.");
    alert("Manual corrections saved successfully.");
  };

  // Update specific values and log changes
  const updatePatientField = (
    field: "name" | "dob" | "gender" | "mrn",
    newVal: string,
    setter: React.Dispatch<React.SetStateAction<ExtractedValue>>,
    currVal: ExtractedValue
  ) => {
    if (newVal !== currVal.value) {
      setter({ ...currVal, value: newVal, confidence: 1.0 }); // mark as 100% since human corrected it!
      logAudit(`Changed Patient ${field} from '${currVal.value}' to '${newVal}'.`);
    }
  };

  const updateObservationField = (
    obsIndex: number,
    col: "analyte_name" | "value" | "unit" | "reference_range",
    newVal: string
  ) => {
    const currVal = observations[obsIndex][col];
    if (newVal !== currVal.value) {
      const updated = [...observations];
      updated[obsIndex][col] = { ...currVal, value: newVal, confidence: 1.0 };
      setObservations(updated);
      logAudit(`Changed Obs [${obsIndex}] ${col} from '${currVal.value}' to '${newVal}'.`);
    }
  };

  // Resolve AI explanation depending on focused field
  const getExplanation = (): { title: string; text: string; evidence: string; confidence: number } => {
    if (selectedField === "documentType") {
      return {
        title: "Document Classification Explanation",
        text: "The classification model matched the large uppercase header keywords 'CLINICAL PATHOLOGY' and 'REPORT' to identify a standard laboratory diagnostics report.",
        evidence: documentType.evidence,
        confidence: documentType.confidence,
      };
    }
    if (selectedField.startsWith("patient.")) {
      const field = selectedField.split(".")[1];
      if (field === "name") {
        return {
          title: "Patient Name Extraction",
          text: "Patient demographics card parsed. Identified name sequence following the literal label anchor string 'Patient Name:'.",
          evidence: patientName.evidence,
          confidence: patientName.confidence,
        };
      }
      if (field === "dob") {
        return {
          title: "Date of Birth Normalization",
          text: "Regex parser extracted '01/01/1990' and ISO standardized it to '1990-01-01'. Matches the label DOB.",
          evidence: patientDob.evidence,
          confidence: patientDob.confidence,
        };
      }
      if (field === "gender") {
        return {
          title: "Gender Classification",
          text: "Sex code 'M' mapped to HL7 administrative gender 'Male'.",
          evidence: patientGender.evidence,
          confidence: patientGender.confidence,
        };
      }
      if (field === "mrn") {
        return {
          title: "MRN Extraction Alert",
          text: "Lower confidence detected because of faint scan pixels on the right-hand header label. Reviewer check suggested.",
          evidence: patientMrn.evidence,
          confidence: patientMrn.confidence,
        };
      }
    }
    if (selectedField.startsWith("observations.")) {
      const parts = selectedField.split(".");
      const idx = parseInt(parts[1]);
      const col = parts[2];
      const obs = observations[idx];
      const fieldObj = obs[col as keyof ObservationRow] as ExtractedValue;
      return {
        title: `Observation [${obs.analyte_name.value}] - ${col}`,
        text: `Extracted grid table cell row index ${idx} matching the column headers in reading order.`,
        evidence: fieldObj?.evidence || obs.value.evidence,
        confidence: fieldObj?.confidence || obs.value.confidence,
      };
    }
    return {
      title: "AI Extraction Panel",
      text: "Select any data field on the right form or hover over highlights to display the AI confidence analytics.",
      evidence: "None",
      confidence: 1.0,
    };
  };

  const exp = getExplanation();

  const getConfidenceClass = (conf: number) => {
    if (conf >= 0.90) return "confidence-high";
    if (conf >= 0.70) return "confidence-medium";
    return "confidence-low";
  };

  return (
    <div className="app-container">
      {/* Header Panel */}
      <header className="header">
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <h1 className="workspace-title">DigiFax Reviewer Workspace</h1>
          <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
            ID: {documentId}
          </span>
        </div>
        
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <span className={`confidence-badge ${status === "approved" ? "confidence-high" : status === "rejected" ? "confidence-low" : "confidence-medium"}`}>
            STATUS: {status.toUpperCase()}
          </span>
          <button className="btn btn-secondary" onClick={handleSave}>Save Corrections</button>
          <button className="btn btn-danger" onClick={handleReject}>Reject</button>
          <button className="btn btn-primary" onClick={handleApprove}>Approve</button>
        </div>
      </header>

      {/* Main Workspace Layout */}
      <main className="main-content">
        
        {/* Left Column: PDF Viewer with Highlight Overlays */}
        <section className="left-panel">
          <div className="pdf-container" ref={pdfContainerRef}>
            <div className="pdf-viewport" style={{ width: "600px", height: "800px", position: "relative" }}>
              
              {/* Simulated Paper Layout Render */}
              <div style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
                backgroundColor: "#fff",
                color: "#1e293b",
                padding: "40px",
                fontFamily: "serif",
                fontSize: "12px"
              }}>
                <div style={{ textAlign: "center", borderBottom: "2px solid #334155", paddingBottom: "10px", marginBottom: "20px" }}>
                  <h2 style={{ fontSize: "16px", textTransform: "uppercase" }}>Clinical Pathology Laboratory Report</h2>
                  <p style={{ fontSize: "10px", color: "#64748b" }}>100 Medical Plaza, Suite 400 | Tel: (555) 019-2834</p>
                </div>

                {/* Patient Information Card Grid */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", border: "1px solid #cbd5e1", padding: "12px", borderRadius: "4px", marginBottom: "30px" }}>
                  <div>
                    <p><strong>Patient Name:</strong> John Doe</p>
                    <p style={{ marginTop: "6px" }}><strong>DOB:</strong> 01/01/1990</p>
                  </div>
                  <div>
                    <p><strong>Sex:</strong> M</p>
                    <p style={{ marginTop: "6px" }}><strong>MRN:</strong> 12345</p>
                  </div>
                </div>

                {/* Clinical Observation Tables */}
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "11px" }}>
                  <thead>
                    <tr style={{ borderBottom: "2px solid #cbd5e1", textAlign: "left" }}>
                      <th style={{ padding: "8px" }}>Analyte</th>
                      <th style={{ padding: "8px" }}>Value</th>
                      <th style={{ padding: "8px" }}>Unit</th>
                      <th style={{ padding: "8px" }}>Ref Range</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr style={{ borderBottom: "1px solid #e2e8f0" }}>
                      <td style={{ padding: "10px 8px" }}>Fasting Glucose</td>
                      <td style={{ padding: "10px 8px" }}>145</td>
                      <td style={{ padding: "10px 8px" }}>mg/dL</td>
                      <td style={{ padding: "10px 8px" }}>Normal: 70 - 100 mg/dL</td>
                    </tr>
                    <tr style={{ borderBottom: "1px solid #e2e8f0" }}>
                      <td style={{ padding: "10px 8px" }}>Total Cholesterol</td>
                      <td style={{ padding: "10px 8px" }}>240</td>
                      <td style={{ padding: "10px 8px" }}>mg/dL</td>
                      <td style={{ padding: "10px 8px" }}>Desirable: &lt;200</td>
                    </tr>
                  </tbody>
                </table>

                {/* Footer Validation Stamp */}
                <div style={{ marginTop: "180px", borderTop: "1px solid #cbd5e1", paddingTop: "15px" }}>
                  <p style={{ fontSize: "10px", color: "#64748b" }}>Electronically signed by Albert Schweitzer, MD</p>
                  <p style={{ fontSize: "9px", color: "#94a3b8", marginTop: "4px" }}>Verification Hash: sha256-8f3a9e227bc</p>
                </div>
              </div>

              {/* Dynamic Coordinate Bounding Box Overlays */}
              {Object.entries(boundingBoxes).map(([fieldKey, coords]) => (
                <div
                  key={fieldKey}
                  className={`bounding-box ${selectedField === fieldKey ? "active" : ""} ${
                    fieldKey === "patient.mrn" ? "low-confidence" : ""
                  }`}
                  style={{
                    left: coords.left,
                    top: coords.top,
                    width: coords.width,
                    height: coords.height
                  }}
                  onClick={() => setSelectedField(fieldKey)}
                />
              ))}

            </div>
          </div>
        </section>

        {/* Right Column: Interactive Editor Form */}
        <section className="right-panel">
          
          {/* Document Properties */}
          <div className="editor-section">
            <h2 className="section-header">Document Classification</h2>
            <div className="form-group">
              <div className="form-label-row">
                <span className="form-label">Classification Tag</span>
                <span className={`confidence-badge ${getConfidenceClass(documentType.confidence)}`}>
                  {(documentType.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <div className="input-container">
                <input
                  type="text"
                  className="form-input"
                  value={documentType.value}
                  onChange={(e) => setDocumentType({ ...documentType, value: e.target.value })}
                  onFocus={() => setSelectedField("documentType")}
                />
              </div>
            </div>
          </div>

          {/* Demographics Card */}
          <div className="editor-section">
            <h2 className="section-header">Patient Demographics</h2>
            <div className="form-grid">
              
              <div className="form-group">
                <div className="form-label-row">
                  <span className="form-label">Patient Name</span>
                  <span className={`confidence-badge ${getConfidenceClass(patientName.confidence)}`}>
                    {(patientName.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="input-container">
                  <input
                    type="text"
                    className="form-input"
                    value={patientName.value}
                    onChange={(e) => updatePatientField("name", e.target.value, setPatientName, patientName)}
                    onFocus={() => setSelectedField("patient.name")}
                  />
                </div>
              </div>

              <div className="form-group">
                <div className="form-label-row">
                  <span className="form-label">Date of Birth (DOB)</span>
                  <span className={`confidence-badge ${getConfidenceClass(patientDob.confidence)}`}>
                    {(patientDob.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="input-container">
                  <input
                    type="text"
                    className="form-input"
                    value={patientDob.value}
                    onChange={(e) => updatePatientField("dob", e.target.value, setPatientDob, patientDob)}
                    onFocus={() => setSelectedField("patient.dob")}
                  />
                </div>
              </div>

              <div className="form-group">
                <div className="form-label-row">
                  <span className="form-label">Sex/Gender</span>
                  <span className={`confidence-badge ${getConfidenceClass(patientGender.confidence)}`}>
                    {(patientGender.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="input-container">
                  <input
                    type="text"
                    className="form-input"
                    value={patientGender.value}
                    onChange={(e) => updatePatientField("gender", e.target.value, setPatientGender, patientGender)}
                    onFocus={() => setSelectedField("patient.gender")}
                  />
                </div>
              </div>

              <div className="form-group">
                <div className="form-label-row">
                  <span className="form-label">Medical Record Number (MRN)</span>
                  <span className={`confidence-badge ${getConfidenceClass(patientMrn.confidence)}`}>
                    {(patientMrn.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="input-container">
                  <input
                    type="text"
                    className="form-input"
                    value={patientMrn.value}
                    onChange={(e) => updatePatientField("mrn", e.target.value, setPatientMrn, patientMrn)}
                    onFocus={() => setSelectedField("patient.mrn")}
                  />
                </div>
              </div>

            </div>
          </div>

          {/* Observations Form Grid Table */}
          <div className="editor-section">
            <h2 className="section-header">Clinical Observations</h2>
            <table className="observations-table">
              <thead>
                <tr>
                  <th>Analyte</th>
                  <th>Value</th>
                  <th>Unit</th>
                  <th>Ref Range</th>
                </tr>
              </thead>
              <tbody>
                {observations.map((obs, idx) => (
                  <tr key={obs.id}>
                    <td>
                      <input
                        type="text"
                        className="table-input"
                        value={obs.analyte_name.value}
                        onChange={(e) => updateObservationField(idx, "analyte_name", e.target.value)}
                        onFocus={() => setSelectedField(`observations.${idx}.analyte_name`)}
                      />
                    </td>
                    <td>
                      <input
                        type="text"
                        className="table-input"
                        value={obs.value.value}
                        onChange={(e) => updateObservationField(idx, "value", e.target.value)}
                        onFocus={() => setSelectedField(`observations.${idx}.value`)}
                      />
                    </td>
                    <td>
                      <input
                        type="text"
                        className="table-input"
                        value={obs.unit.value}
                        onChange={(e) => updateObservationField(idx, "unit", e.target.value)}
                        onFocus={() => setSelectedField(`observations.${idx}.unit`)}
                      />
                    </td>
                    <td>
                      <input
                        type="text"
                        className="table-input"
                        value={obs.reference_range.value}
                        onChange={(e) => updateObservationField(idx, "reference_range", e.target.value)}
                        onFocus={() => setSelectedField(`observations.${idx}.reference_range`)}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* AI Explanations */}
          <div className="editor-section">
            <h2 className="section-header">AI Extraction Details</h2>
            <div className="explanation-panel">
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                <span className="explanation-title">{exp.title}</span>
                <span className={`confidence-badge ${getConfidenceClass(exp.confidence)}`}>
                  {(exp.confidence * 100).toFixed(0)}% Confidence
                </span>
              </div>
              <p className="explanation-text">{exp.text}</p>
              {exp.evidence !== "None" && (
                <div>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "block", marginTop: "12px", fontWeight: 600 }}>
                    Extracted Evidence Span:
                  </span>
                  <span className="evidence-span">{exp.evidence}</span>
                </div>
              )}
            </div>
          </div>

          {/* Audit Trail List */}
          <div className="editor-section" style={{ borderBottom: "none" }}>
            <h2 className="section-header">Audit Trail logs</h2>
            <div className="audit-list">
              {auditTrail.map((log, index) => (
                <div className="audit-item" key={index}>
                  <span className="audit-timestamp">[{log.timestamp}]</span>
                  <span>{log.message}</span>
                </div>
              ))}
            </div>
          </div>

        </section>
      </main>

      {/* Footer Hotkeys Cheat Sheet */}
      <footer className="footer-shortcuts">
        <span>Keyboard Shortcuts:</span>
        <span><kbd className="shortcut-key">Ctrl + S</kbd> Save changes</span>
        <span><kbd className="shortcut-key">Ctrl + Enter</kbd> Approve report</span>
        <span><kbd className="shortcut-key">Ctrl + Backspace</kbd> Reject report</span>
        <span><kbd className="shortcut-key">Tab</kbd> Navigate inputs</span>
      </footer>
    </div>
  );
}

export default App;
