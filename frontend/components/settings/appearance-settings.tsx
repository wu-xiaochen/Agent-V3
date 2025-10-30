"use client"

import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { useAppStore } from "@/lib/store"

export function AppearanceSettings() {
  const { darkMode, setDarkMode } = useAppStore()

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div>
          <Label>Theme</Label>
          <RadioGroup 
            value={darkMode ? "dark" : "light"} 
            onValueChange={(value) => setDarkMode(value === "dark")}
            className="mt-2"
          >
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="light" id="light" />
              <Label htmlFor="light" className="font-normal cursor-pointer">
                Light
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="dark" id="dark" />
              <Label htmlFor="dark" className="font-normal cursor-pointer">
                Dark
              </Label>
            </div>
          </RadioGroup>
        </div>
      </div>
    </div>
  )
}

