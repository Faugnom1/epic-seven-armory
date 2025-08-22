import React, { useEffect, useState } from 'react';

export default function ScanToggle() {
  const [on, setOn] = useState(false);
  const [busy, setBusy] = useState(false);
  const [found, setFound] = useState(false);

  useEffect(() => {
    if (!window.api || !window.api.onMonitorStatus) return;
    const unsubscribe = window.api.onMonitorStatus((status) => {
      if (status && typeof status.enabled === 'boolean') setOn(Boolean(status.enabled));
      if (status && typeof status.found === 'boolean') setFound(Boolean(status.found));
    });
    return () => { if (unsubscribe) unsubscribe(); };
  }, []);

  const toggle = async () => {
    if (busy) return;
    setBusy(true);
    try {
      // 1) Keep existing Electron monitor behavior
      if (window.api && window.api.toggleMonitor) {
        const res = await window.api.toggleMonitor(!on);
        if (res && typeof res.enabled === 'boolean') {
          setOn(Boolean(res.enabled));
        } else {
          setOn((prev) => !prev);
        }
      } else {
        setOn((prev) => !prev);
      }

      // 2) Also start/stop the backend OCR scanner
      const username = localStorage.getItem("epic_seven_account") || "";
      try {
        await fetch("http://localhost:5000/scanner", {
          method: "POST",
          headers: { "Content-Type": "application/json", username },
          body: JSON.stringify({ enabled: !on })
        });
      } catch (e) {
        console.warn("[ScanToggle] /scanner call failed (hero scanner)", e);
      }
    } catch (e) {
      console.error('[ScanToggle] toggle error:', e);
      setOn((prev) => !prev);
    } finally {
      setBusy(false);
    }
  };

  const stateClass = on ? (found ? 'is-on ok' : 'is-on warn') : '';

  return (
    <button
      className={`scan-toggle ${stateClass}`}
      onClick={toggle}
      disabled={busy}
      title={
        on
          ? (found ? 'Scanning Epic Seven window (found)' : 'Scanning Epic Seven window (not found)')
          : 'Start scanning Epic Seven window'
      }
    >
      <span className={`dot ${found ? 'ok' : (on ? 'warn' : '')}`} />
      <span className="label">
        {on ? (
          <>
            Scanning:{' '}
            <span className="status">
              {found ? (
                <span className="status-ok">Epic 7 Windows Found</span>
              ) : (
                <span className="status-warn">Epic 7 Window Not Found</span>
              )}
            </span>
          </>
        ) : (
          'Scan Off'
        )}
      </span>
    </button>
  );
}
