import { useState } from "react";
import "./toggle.css";

export default function Page() {
  const [enabled, setEnabled] = useState<boolean>(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEnabled(e.target.checked);
  };

  return (
    <main className="min-h-screen bg-white text-black dark:bg-black dark:text-white transition-colors duration-200">
      <div className="flex flex-col items-center justify-center h-screen gap-6">
        <p className="text-lg">hello</p>
        {/* TOGGLE */}
        <label className="switch">
          <input
            type="checkbox"
            checked={enabled}
            onChange={handleChange}
          />
          <span className="slider round"></span>
        </label>
        <p>{enabled ? "ON" : "OFF"}</p>
      </div>
    </main>
  );
}