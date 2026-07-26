"use client";

import { useEffect } from "react";

export function ServiceWorkerRegister() {
  useEffect(() => {
    if (typeof window !== "undefined" && "serviceWorker" in navigator) {
      window.addEventListener("load", () => {
        navigator.serviceWorker
          .register("/sw.js")
          .then((registration) => {
            console.log("[Service Worker] Registered successfully with scope:", registration.scope);
          })
          .catch((err) => {
            console.error("[Service Worker] Registration failed:", err);
          });
      });
    }
  }, []);

  return null;
}
export default ServiceWorkerRegister;
