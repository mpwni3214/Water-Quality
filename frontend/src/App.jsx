import React, { useState, useEffect } from 'react';
import {
  Droplets,
  ShieldCheck,
  ShieldAlert,
  Sparkles,
  RefreshCw,
  Activity,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  History,
  TrendingUp,
  Cpu,
  Layers,
  Info
} from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000/api';

const DEFAULT_INPUTS = {
  ph: '7.08',
  Hardness: '196.37',
  Solids: '22014.09',
  Chloramines: '7.12',
  Sulfate: '333.78',
  Conductivity: '426.21',
  Organic_carbon: '14.28',
  Trihalomethanes: '66.40',
  Turbidity: '3.97',
};

const FEATURE_METADATA = [
  { key: 'ph', name: 'Độ pH', unit: 'pH', standard: '6.5 - 8.5', step: '0.01', desc: 'Độ axit/kiềm của nước (0-14)' },
  { key: 'Hardness', name: 'Độ cứng (Hardness)', unit: 'mg/L', standard: '< 300 mg/L', step: '0.1', desc: 'Hàm lượng ion Ca²⁺ và Mg²⁺' },
  { key: 'Solids', name: 'Chất rắn hòa tan (TDS)', unit: 'ppm', standard: '< 1000 ppm', step: '1', desc: 'Tổng lượng khoáng chất & muối' },
  { key: 'Chloramines', name: 'Chloramines', unit: 'ppm', standard: '< 4.0 ppm', step: '0.01', desc: 'Chất khử trùng bảo vệ nước' },
  { key: 'Sulfate', name: 'Nồng độ Sunfat (Sulfate)', unit: 'mg/L', standard: '< 250 mg/L', step: '0.1', desc: 'Muối sunfat tự nhiên trong đất đá' },
  { key: 'Conductivity', name: 'Độ dẫn điện (EC)', unit: 'μS/cm', standard: '< 400 μS/cm', step: '1', desc: 'Khả năng dẫn điện của các ion' },
  { key: 'Organic_carbon', name: 'Cacbon hữu cơ (TOC)', unit: 'ppm', standard: '< 4.0 ppm', step: '0.01', desc: 'Chỉ số chất hữu cơ trong nước' },
  { key: 'Trihalomethanes', name: 'Trihalomethanes (THMs)', unit: 'μg/L', standard: '< 80 μg/L', step: '0.1', desc: 'Phụ phẩm clo hóa có nguy cơ độc' },
  { key: 'Turbidity', name: 'Độ đục (Turbidity)', unit: 'NTU', standard: '< 5.0 NTU', step: '0.01', desc: 'Đo độ trong suốt và cặn lơ lửng' },
];

export default function App() {
  const [formData, setFormData] = useState(DEFAULT_INPUTS);
  const [presets, setPresets] = useState([]);
  const [modelStats, setModelStats] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [history, setHistory] = useState(() => {
    try {
      const saved = localStorage.getItem('water_quality_history');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // Fetch presets and model stats on load
  useEffect(() => {
    fetchPresets();
    fetchStats();
  }, []);

  const fetchPresets = async () => {
    try {
      const res = await fetch(`${API_BASE}/presets/`);
      if (res.ok) {
        const data = await res.json();
        if (data.presets) setPresets(data.presets);
      }
    } catch (e) {
      console.warn('Could not fetch remote presets, using offline presets fallback.');
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/stats/`);
      if (res.ok) {
        const data = await res.json();
        setModelStats(data);
      }
    } catch (e) {
      console.warn('Could not fetch stats');
    }
  };

  const handleInputChange = (key, value) => {
    setFormData((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const applyPreset = (presetValues) => {
    const formatted = {};
    Object.keys(DEFAULT_INPUTS).forEach((k) => {
      formatted[k] = presetValues[k] !== undefined ? String(presetValues[k]) : '';
    });
    setFormData(formatted);
    setErrorMsg('');
  };

  const handleReset = () => {
    setFormData(DEFAULT_INPUTS);
    setResult(null);
    setErrorMsg('');
  };

  const handlePredict = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setErrorMsg('');

    try {
      const payload = {};
      Object.keys(formData).forEach((k) => {
        const val = formData[k];
        payload[k] = val !== '' ? parseFloat(val) : null;
      });

      const res = await fetch(`${API_BASE}/predict/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error || `Lỗi máy chủ (${res.status})`);
      }

      const data = await res.json();
      setResult(data);

      // Save to history
      const historyItem = {
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        is_potable: data.is_potable,
        potability_score: data.potability_score,
        status_title: data.status_title,
        inputs: { ...formData },
      };

      setHistory((prev) => {
        const updated = [historyItem, ...prev.slice(0, 7)];
        try {
          localStorage.setItem('water_quality_history', JSON.stringify(updated));
        } catch {}
        return updated;
      });
    } catch (err) {
      setErrorMsg(err.message || 'Không thể kết nối đến máy chủ Django.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="brand-badge">
          <Droplets size={16} />
          Hệ Thống Phân Tích Thông Minh
        </div>
        <h1 className="brand-title">Đánh Giá Chất Lượng Nước</h1>
        <p className="brand-subtitle">
          Dự đoán độ an toàn uống được (Potability) dựa trên mô hình <strong>XGBoost Machine Learning</strong>{' '}
          kết hợp đối chiếu tiêu chuẩn an toàn nước sạch WHO & Bộ Y Tế.
        </p>
      </header>

      {/* Main Grid */}
      <div className="main-grid">
        {/* Left Column: Form & Presets */}
        <section className="glass-card">
          <div className="card-title">
            <Activity className="card-title-icon" size={22} />
            Nhập Các Chỉ Số Hóa Sinh Của Nước
          </div>
          <p className="card-subtitle">
            Nhập 9 thông số cảm quan và hóa sinh của mẫu nước, hoặc chọn nhanh các mẫu thử nghiệm có sẵn bên dưới.
          </p>

          {/* Presets */}
          <div className="presets-section">
            <div className="presets-label">
              <Sparkles size={14} /> Mẫu nước thực nghiệm nhanh
            </div>
            <div className="presets-grid">
              {presets.length > 0 ? (
                presets.map((p) => (
                  <button
                    key={p.id}
                    type="button"
                    className="preset-btn"
                    onClick={() => applyPreset(p.values)}
                    title={p.desc}
                  >
                    <span className="preset-btn-title">{p.title}</span>
                    <span className="preset-btn-desc">{p.desc}</span>
                  </button>
                ))
              ) : (
                <>
                  <button
                    type="button"
                    className="preset-btn"
                    onClick={() =>
                      applyPreset({
                        ph: 7.25,
                        Hardness: 180.5,
                        Solids: 18500,
                        Chloramines: 6.2,
                        Sulfate: 310,
                        Conductivity: 390,
                        Organic_carbon: 11.5,
                        Trihalomethanes: 55,
                        Turbidity: 3.1,
                      })
                    }
                  >
                    <span className="preset-btn-title">Nước uống đạt chuẩn</span>
                    <span className="preset-btn-desc">Mẫu nước an toàn theo WHO</span>
                  </button>
                  <button
                    type="button"
                    className="preset-btn"
                    onClick={() =>
                      applyPreset({
                        ph: 5.2,
                        Hardness: 240,
                        Solids: 35000,
                        Chloramines: 9.8,
                        Sulfate: 410,
                        Conductivity: 620,
                        Organic_carbon: 22.4,
                        Trihalomethanes: 105,
                        Turbidity: 5.8,
                      })
                    }
                  >
                    <span className="preset-btn-title">Nước ô nhiễm hữu cơ</span>
                    <span className="preset-btn-desc">Dư lượng Clo và THMs cao</span>
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handlePredict}>
            <div className="form-grid">
              {FEATURE_METADATA.map((feat) => (
                <div key={feat.key} className="input-group">
                  <div className="input-label-row">
                    <label htmlFor={feat.key} className="input-label" title={feat.desc}>
                      {feat.name}
                    </label>
                    <span className="input-standard">{feat.standard}</span>
                  </div>
                  <div className="input-wrapper">
                    <input
                      id={feat.key}
                      type="number"
                      step={feat.step}
                      className="input-field"
                      value={formData[feat.key]}
                      onChange={(e) => handleInputChange(feat.key, e.target.value)}
                      placeholder="Nhập giá trị..."
                      required
                    />
                    <span className="input-unit">{feat.unit}</span>
                  </div>
                </div>
              ))}
            </div>

            {errorMsg && (
              <div style={{ marginTop: '1rem', color: '#fb7185', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <AlertTriangle size={18} /> {errorMsg}
              </div>
            )}

            <div className="form-actions">
              <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? (
                  <>
                    <RefreshCw size={18} className="spin" /> Đang phân tích mẫu...
                  </>
                ) : (
                  <>
                    <Sparkles size={18} /> Đánh Giá Chất Lượng Nước
                  </>
                )}
              </button>
              <button type="button" className="btn-secondary" onClick={handleReset} title="Khôi phục giá trị trung bình">
                <RefreshCw size={16} /> Đặt lại
              </button>
            </div>
          </form>
        </section>

        {/* Right Column: Prediction Results */}
        <section className="glass-card">
          <div className="card-title">
            <TrendingUp className="card-title-icon" size={22} />
            Kết Quả Phân Tích & Chẩn Đoán
          </div>
          <p className="card-subtitle">
            Đánh giá tổng hợp từ thuật toán Gradient Boosting kết hợp phân tích ngưỡng từng chỉ số.
          </p>

          {result ? (
            <div>
              {/* Status Header Box */}
              <div className={`result-box ${result.status_color}`}>
                <div className="result-status-header">
                  <div className="status-badge-icon">
                    {result.is_potable ? <ShieldCheck size={30} /> : <ShieldAlert size={30} />}
                  </div>
                  <div>
                    <h2 className="status-title-text">{result.status_title}</h2>
                    <p className="status-summary-text">{result.summary}</p>
                  </div>
                </div>

                {/* Potability Probability Gauge */}
                <div className="gauge-wrapper">
                  <div className="gauge-header">
                    <span className="gauge-label">Mức độ an toàn uống được (Potability Score):</span>
                    <span className="gauge-value" style={{ color: result.is_potable ? '#34d399' : '#fb7185' }}>
                      {result.potability_score}%
                    </span>
                  </div>
                  <div className="gauge-track">
                    <div
                      className={`gauge-bar ${result.status_color}`}
                      style={{ width: `${Math.min(100, Math.max(5, result.potability_score))}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Actionable Recommendations */}
              {result.recommendations && result.recommendations.length > 0 && (
                <div className="recs-box">
                  <div className="recs-title">
                    <CheckCircle2 size={18} color="#38bdf8" /> Đề xuất xử lý & khuyến cáo kỹ thuật
                  </div>
                  <ul className="recs-list">
                    {result.recommendations.map((rec, idx) => (
                      <li key={idx} className="recs-item">
                        <span className="recs-item-icon">
                          {result.is_potable ? (
                            <CheckCircle2 size={16} color="#34d399" />
                          ) : (
                            <AlertTriangle size={16} color="#f59e0b" />
                          )}
                        </span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Detailed Breakdown of 9 Parameters */}
              <div style={{ marginTop: '1.5rem' }}>
                <div style={{ fontSize: '0.92rem', fontWeight: 700, color: '#f1f5f9', marginBottom: '0.65rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Layers size={16} color="#38bdf8" /> Chi tiết 9 chỉ tiêu theo quy chuẩn WHO
                </div>
                <div className="param-list">
                  {result.metrics_evaluation &&
                    result.metrics_evaluation.map((m) => (
                      <div key={m.key} className={`param-card ${m.status}`}>
                        <div className="param-card-header">
                          <span className="param-card-title">{m.name}</span>
                          <span className={`status-chip ${m.status}`}>{m.status_label}</span>
                        </div>
                        <div>
                          <span className="param-card-value">
                            {m.value !== null ? m.value : 'N/A'}
                          </span>
                          <span className="param-card-unit">{m.unit}</span>
                        </div>
                        <p className="param-card-desc">{m.message}</p>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <Droplets size={54} className="empty-state-icon" />
              <h3 style={{ color: '#e2e8f0', marginBottom: '0.5rem', fontWeight: 600 }}>Chưa có kết quả dự đoán</h3>
              <p className="empty-state-text">
                Hãy nhấn nút <strong>"Đánh Giá Chất Lượng Nước"</strong> hoặc chọn một trong các mẫu có sẵn ở cột bên trái để bắt đầu phân tích.
              </p>
            </div>
          )}
        </section>
      </div>

      {/* History Section */}
      {history.length > 0 && (
        <section className="history-section glass-card">
          <div className="card-title">
            <History className="card-title-icon" size={20} />
            Lịch Sử Các Lần Đánh Giá Gần Đây
          </div>
          <p className="card-subtitle">Nhấp vào một mẫu trước đó để xem lại thông số đã kiểm tra.</p>

          <div className="history-grid">
            {history.map((item) => (
              <div
                key={item.id}
                className="history-card"
                onClick={() => {
                  setFormData(item.inputs);
                  handlePredict();
                }}
              >
                <div className="history-card-header">
                  <span
                    className={`status-chip ${item.is_potable ? 'safe' : 'danger'}`}
                    style={{ fontSize: '0.68rem' }}
                  >
                    {item.is_potable ? 'An Toàn' : 'Không Đạt'}
                  </span>
                  <span className="history-card-time">{item.timestamp}</span>
                </div>
                <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#f8fafc', marginBottom: '0.3rem' }}>
                  Xác suất: {item.potability_score}%
                </div>
                <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                  pH: {item.inputs.ph} | Độ đục: {item.inputs.Turbidity} NTU | TDS: {item.inputs.Solids}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Model Information Footer */}
      <footer className="stats-footer">
        <div>
          <strong>Mô hình AI:</strong> {modelStats ? modelStats.model_name : 'XGBoost Classifier (1000 cây quyết định)'}
        </div>
        <div className="stats-badges">
          <span className="stats-pill">
            <Cpu size={13} style={{ display: 'inline', marginRight: '4px' }} />
            XGBoost 3.x + Scikit-Learn
          </span>
          <span className="stats-pill">
            <Layers size={13} style={{ display: 'inline', marginRight: '4px' }} />
            9 Đặc trưng thủy văn
          </span>
          <span className="stats-pill">
            <Info size={13} style={{ display: 'inline', marginRight: '4px' }} />
            Chuẩn WHO / QCVN 01-1:2018/BYT
          </span>
        </div>
      </footer>
    </div>
  );
}

