"use client";

import { useEffect, useState } from "react";

interface SettingsData {
  subscribe_and_save_discount_percent: number;
  environment: string;
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsData | null>(null);

  useEffect(() => {
    fetch("/api/admin/settings")
      .then((r) => r.json())
      .then((d) => setSettings(d));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Settings</h1>
      {settings && (
        <div className="space-y-4 max-w-md">
          <div className="rounded-lg border p-4">
            <label className="text-sm font-medium">Subscribe & Save Discount</label>
            <p className="text-2xl font-bold">{settings.subscribe_and_save_discount_percent}%</p>
          </div>
          <div className="rounded-lg border p-4">
            <label className="text-sm font-medium">Environment</label>
            <p className="text-lg font-medium">{settings.environment}</p>
          </div>
        </div>
      )}
    </div>
  );
}
