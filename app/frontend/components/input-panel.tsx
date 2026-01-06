"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";

export interface PredictionInputData {
  building_id: number;
  meter: number;
  site_id: number;
  primary_use: string;
  square_feet: number;
  air_temperature: number;
  cloud_coverage: number;
  dew_temperature: number;
  precip_depth_1_hr: number;
  sea_level_pressure: number;
  wind_direction: number;
  wind_speed: number;
  day: number;
  month: number;
  week: number;
  hour: number;
  is_weekend: number;
}

interface InputPanelProps {
  onPredict: (inputs: PredictionInputData) => void;
  isLoading: boolean;
}

export default function InputPanel({ onPredict, isLoading }: InputPanelProps) {
  const [formData, setFormData] = useState({
    building_id: 0,
    site_id: 0,
    primary_use: "Office",
    square_feet: 1000,
    meter: 0,
    air_temperature: 20.0,
    dew_temperature: 15.0,
    cloud_coverage: 4,
    wind_speed: 5.0,
    wind_direction: 180,
    sea_level_pressure: 1013,
    precip_depth_1_hr: 0,
    selectedDate: new Date(),
    day: new Date().getDate(),
    month: new Date().getMonth() + 1,
    week: getWeekOfYear(new Date()),
    hour: 12,
    is_weekend: [0, 6].includes(new Date().getDay()) ? 1 : 0,
  });

  function getWeekOfYear(date: Date): number {
    const firstDayOfYear = new Date(date.getFullYear(), 0, 1);
    const pastDaysOfYear =
      (date.getTime() - firstDayOfYear.getTime()) / 86400000;
    return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7);
  }

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedDate = new Date(e.target.value);
    const day = selectedDate.getDate();
    const month = selectedDate.getMonth() + 1;
    const week = getWeekOfYear(selectedDate);
    const is_weekend = [0, 6].includes(selectedDate.getDay()) ? 1 : 0;

    setFormData((prev) => ({
      ...prev,
      selectedDate,
      day,
      month,
      week,
      is_weekend,
    }));
  };

  const handleSliderChange = (key: string, value: number[]) => {
    setFormData((prev) => ({ ...prev, [key]: value[0] }));
  };

  const handleInputChange = (key: string, value: string) => {
    if (value === "") {
      setFormData((prev) => ({ ...prev, [key]: "" }));
      return;
    }

    if (key === "primary_use") {
      setFormData((prev) => ({ ...prev, [key]: value }));
    } else {
      const numValue = Number(value);
      if (!isNaN(numValue)) {
        setFormData((prev) => ({ ...prev, [key]: numValue }));
      }
    }
  };

  const handleInputFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    e.target.select();
  };

  const handleInputBlur = (key: string, min: number = 0) => {
    const currentValue = formData[key as keyof typeof formData];
    if (
      currentValue === "" ||
      (typeof currentValue === "number" && currentValue < min)
    ) {
      setFormData((prev) => ({ ...prev, [key]: min }));
    }
  };

  const handlePredict = () => {
    const inputs = {
      building_id: Number(formData.building_id) || 0,
      site_id: formData.site_id,
      primary_use: formData.primary_use,
      square_feet: Number(formData.square_feet) || 100000,
      meter: formData.meter,
      air_temperature: formData.air_temperature,
      dew_temperature: formData.dew_temperature,
      cloud_coverage: formData.cloud_coverage,
      wind_speed: formData.wind_speed,
      wind_direction: formData.wind_direction,
      sea_level_pressure: formData.sea_level_pressure,
      precip_depth_1_hr: formData.precip_depth_1_hr,
      day: formData.day,
      month: formData.month,
      week: formData.week,
      hour: formData.hour,
      is_weekend: formData.is_weekend,
    };
    onPredict(inputs);
  };

  return (
    <Card className="bg-card border-border mb-6">
      <CardHeader>
        <CardTitle className="text-lg font-light text-foreground">
          Input Configuration
        </CardTitle>
        <CardDescription className="text-muted-foreground">
          Configure prediction parameters
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-[#ea580c] mb-4">
              Meter Data
            </h3>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">
                Site ID (0-15)
              </Label>
              <Select
                value={String(formData.site_id)}
                onValueChange={(value) => handleInputChange("site_id", value)}
              >
                <SelectTrigger className="bg-input border-border text-foreground">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-popover border-border">
                  {Array.from({ length: 16 }, (_, i) => i).map((id) => (
                    <SelectItem
                      key={id}
                      value={String(id)}
                      className="text-popover-foreground"
                    >
                      Site {id}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">
                Building ID (0-1448)
              </Label>
              <Input
                type="number"
                value={formData.building_id}
                onChange={(e) =>
                  handleInputChange("building_id", e.target.value)
                }
                onFocus={handleInputFocus}
                onBlur={() => handleInputBlur("building_id", 0)}
                className="bg-input border-border text-foreground [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                min="0"
                max="1448"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">
                Primary Use
              </Label>
              <Select
                value={formData.primary_use}
                onValueChange={(value) =>
                  handleInputChange("primary_use", value)
                }
              >
                <SelectTrigger className="bg-input border-border text-foreground">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-popover border-border">
                  <SelectItem
                    value="Education"
                    className="text-popover-foreground"
                  >
                    Education
                  </SelectItem>
                  <SelectItem
                    value="Lodging/residential"
                    className="text-popover-foreground"
                  >
                    Lodging/residential
                  </SelectItem>
                  <SelectItem
                    value="Office"
                    className="text-popover-foreground"
                  >
                    Office
                  </SelectItem>
                  <SelectItem
                    value="Entertainment/public assembly"
                    className="text-popover-foreground"
                  >
                    Entertainment/public assembly
                  </SelectItem>
                  <SelectItem value="Other" className="text-popover-foreground">
                    Other
                  </SelectItem>
                  <SelectItem
                    value="Retail"
                    className="text-popover-foreground"
                  >
                    Retail
                  </SelectItem>
                  <SelectItem
                    value="Parking"
                    className="text-popover-foreground"
                  >
                    Parking
                  </SelectItem>
                  <SelectItem
                    value="Public services"
                    className="text-popover-foreground"
                  >
                    Public services
                  </SelectItem>
                  <SelectItem
                    value="Warehouse/storage"
                    className="text-popover-foreground"
                  >
                    Warehouse/storage
                  </SelectItem>
                  <SelectItem
                    value="Food sales and service"
                    className="text-popover-foreground"
                  >
                    Food sales and service
                  </SelectItem>
                  <SelectItem
                    value="Religious worship"
                    className="text-popover-foreground"
                  >
                    Religious worship
                  </SelectItem>
                  <SelectItem
                    value="Healthcare"
                    className="text-popover-foreground"
                  >
                    Healthcare
                  </SelectItem>
                  <SelectItem
                    value="Utility"
                    className="text-popover-foreground"
                  >
                    Utility
                  </SelectItem>
                  <SelectItem
                    value="Technology/science"
                    className="text-popover-foreground"
                  >
                    Technology/science
                  </SelectItem>
                  <SelectItem
                    value="Manufacturing/industrial"
                    className="text-popover-foreground"
                  >
                    Manufacturing/industrial
                  </SelectItem>
                  <SelectItem
                    value="Services"
                    className="text-popover-foreground"
                  >
                    Services
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">
                Square Feet
              </Label>
              <Input
                type="number"
                value={formData.square_feet}
                onChange={(e) =>
                  handleInputChange("square_feet", e.target.value)
                }
                onFocus={handleInputFocus}
                onBlur={() => handleInputBlur("square_feet", 1000)}
                className="bg-input border-border text-foreground [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                min="1000"
                max="1000000"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">
                Meter Type
              </Label>
              <Select
                value={String(formData.meter)}
                onValueChange={(value) => handleInputChange("meter", value)}
              >
                <SelectTrigger className="bg-input border-border text-foreground">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-popover border-border">
                  <SelectItem value="0" className="text-popover-foreground">
                    Electricity
                  </SelectItem>
                  <SelectItem value="1" className="text-popover-foreground">
                    Chilled Water
                  </SelectItem>
                  <SelectItem value="2" className="text-popover-foreground">
                    Steam
                  </SelectItem>
                  <SelectItem value="3" className="text-popover-foreground">
                    Hot Water
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Weather Data */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-[#ea580c] mb-4">
              Weather Data
            </h3>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">
                Air Temperature: {formData.air_temperature.toFixed(1)}°C
              </Label>
              <Slider
                value={[formData.air_temperature]}
                onValueChange={(value) =>
                  handleSliderChange("air_temperature", value)
                }
                min={-20}
                max={50}
                step={0.1}
                className="[&_[role=slider]]:bg-[#ea580c] [&_[role=slider]]:border-[#ea580c]"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">
                Dew Temperature: {formData.dew_temperature.toFixed(1)}°C
              </Label>
              <Slider
                value={[formData.dew_temperature]}
                onValueChange={(value) =>
                  handleSliderChange("dew_temperature", value)
                }
                min={-20}
                max={40}
                step={0.1}
                className="[&_[role=slider]]:bg-[#ea580c] [&_[role=slider]]:border-[#ea580c]"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">
                Cloud Coverage: {formData.cloud_coverage} oktas
              </Label>
              <Slider
                value={[formData.cloud_coverage]}
                onValueChange={(value) =>
                  handleSliderChange("cloud_coverage", value)
                }
                min={0}
                max={8}
                step={1}
                className="[&_[role=slider]]:bg-[#ea580c] [&_[role=slider]]:border-[#ea580c]"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">
                Sea Level Pressure: {formData.sea_level_pressure} mbar
              </Label>
              <Slider
                value={[formData.sea_level_pressure]}
                onValueChange={(value) =>
                  handleSliderChange("sea_level_pressure", value)
                }
                min={950}
                max={1050}
                step={1}
                className="[&_[role=slider]]:bg-[#ea580c] [&_[role=slider]]:border-[#ea580c]"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">
                Wind Speed: {formData.wind_speed.toFixed(1)} m/s
              </Label>
              <Slider
                value={[formData.wind_speed]}
                onValueChange={(value) =>
                  handleSliderChange("wind_speed", value)
                }
                min={0}
                max={30}
                step={0.1}
                className="[&_[role=slider]]:bg-[#ea580c] [&_[role=slider]]:border-[#ea580c]"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">
                Wind Direction: {formData.wind_direction}°
              </Label>
              <Slider
                value={[formData.wind_direction]}
                onValueChange={(value) =>
                  handleSliderChange("wind_direction", value)
                }
                min={0}
                max={360}
                step={1}
                className="[&_[role=slider]]:bg-[#ea580c] [&_[role=slider]]:border-[#ea580c]"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">
                Precipitation: {formData.precip_depth_1_hr.toFixed(1)} mm
              </Label>
              <Slider
                value={[formData.precip_depth_1_hr]}
                onValueChange={(value) =>
                  handleSliderChange("precip_depth_1_hr", value)
                }
                min={0}
                max={50}
                step={0.1}
                className="[&_[role=slider]]:bg-[#ea580c] [&_[role=slider]]:border-[#ea580c]"
              />
            </div>
          </div>

          {/* Temporal Data */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-[#ea580c] mb-4">
              Temporal Data
            </h3>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">
                Select Date
              </Label>
              <Input
                type="date"
                value={formData.selectedDate.toISOString().split("T")[0]}
                onChange={handleDateChange}
                className="bg-input border-border text-foreground"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="bg-muted p-3 rounded-lg border border-border">
                <div className="text-xs text-muted-foreground">
                  Day of Month
                </div>
                <div className="font-medium text-lg text-foreground">
                  {formData.day}
                </div>
              </div>
              <div className="bg-muted p-3 rounded-lg border border-border">
                <div className="text-xs text-muted-foreground">Month</div>
                <div className="font-medium text-lg text-foreground">
                  {formData.month}
                </div>
              </div>
              <div className="bg-muted p-3 rounded-lg border border-border">
                <div className="text-xs text-muted-foreground">
                  Week of Year
                </div>
                <div className="font-medium text-lg text-foreground">
                  {formData.week}
                </div>
              </div>
              <div className="bg-muted p-3 rounded-lg border border-border">
                <div className="text-xs text-muted-foreground">Is Weekend</div>
                <div className="font-medium text-lg text-foreground">
                  {formData.is_weekend ? "Yes" : "No"}
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">
                Hour of Day: {formData.hour}
              </Label>
              <Slider
                value={[formData.hour]}
                onValueChange={(value) => handleSliderChange("hour", value)}
                min={0}
                max={23}
                step={1}
                className="[&_[role=slider]]:bg-[#ea580c] [&_[role=slider]]:border-[#ea580c]"
              />
            </div>
          </div>
        </div>

        {/* Predict Button */}
        <div className="mt-8 flex justify-center">
          <Button
            onClick={handlePredict}
            disabled={isLoading}
            size="lg"
            className="bg-[#ea580c] hover:bg-[#c2410c] text-white px-12 rounded-lg font-light shadow-lg hover:shadow-xl transition-all"
          >
            {isLoading ? (
              <>
                <div className="animate-spin mr-2 h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                Predicting...
              </>
            ) : (
              "Predict Energy Usage"
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
