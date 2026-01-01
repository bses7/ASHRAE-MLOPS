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
    square_feet: 100000,
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
    setFormData((prev) => ({
      ...prev,
      [key]: isNaN(Number(value)) ? value : Number(value),
    }));
  };

  const handleInputFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    if (e.target.value === "0") {
      e.target.select();
    }
  };

  const handlePredict = () => {
    const inputs = {
      building_id: formData.building_id,
      site_id: formData.site_id,
      primary_use: formData.primary_use,
      square_feet: formData.square_feet,
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
    <Card className="lg:col-span-1 border-border bg-card">
      <CardHeader>
        <CardTitle className="text-lg">Input Panel</CardTitle>
        <CardDescription>Configure prediction parameters</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Building Profile */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-foreground">
            Building Profile
          </h3>

          <div className="space-y-2">
            <Label htmlFor="site-id" className="text-sm">
              Site ID (0-15)
            </Label>
            <Select
              value={String(formData.site_id)}
              onValueChange={(value) => handleInputChange("site_id", value)}
            >
              <SelectTrigger id="site-id" className="bg-input border-border">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Array.from({ length: 16 }, (_, i) => i).map((id) => (
                  <SelectItem key={id} value={String(id)}>
                    Site {id}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="building-id" className="text-sm">
              Building ID (0-1448)
            </Label>
            <Input
              id="building-id"
              type="number"
              value={formData.building_id}
              onChange={(e) => handleInputChange("building_id", e.target.value)}
              onFocus={handleInputFocus}
              className="bg-input border-border"
              placeholder="Enter building ID"
              min="0"
              max="1448"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="primary-use" className="text-sm">
              Primary Use
            </Label>
            <Select
              value={formData.primary_use}
              onValueChange={(value) => handleInputChange("primary_use", value)}
            >
              <SelectTrigger id="primary-use" className="bg-input">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Education">Education</SelectItem>
                <SelectItem value="Lodging/residential">
                  Lodging/residential
                </SelectItem>
                <SelectItem value="Office">Office</SelectItem>
                <SelectItem value="Entertainment/public assembly">
                  Entertainment/public assembly
                </SelectItem>
                <SelectItem value="Other">Other</SelectItem>
                <SelectItem value="Retail">Retail</SelectItem>
                <SelectItem value="Parking">Parking</SelectItem>
                <SelectItem value="Public services">Public services</SelectItem>
                <SelectItem value="Warehouse/storage">
                  Warehouse/storage
                </SelectItem>
                <SelectItem value="Food sales and service">
                  Food sales and service
                </SelectItem>
                <SelectItem value="Religious worship">
                  Religious worship
                </SelectItem>
                <SelectItem value="Healthcare">Healthcare</SelectItem>
                <SelectItem value="Utility">Utility</SelectItem>
                <SelectItem value="Technology/science">
                  Technology/science
                </SelectItem>
                <SelectItem value="Manufacturing/industrial">
                  Manufacturing/industrial
                </SelectItem>
                <SelectItem value="Services">Services</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="square-feet" className="text-sm">
              Square Feet
            </Label>
            <Input
              id="square-feet"
              type="number"
              value={formData.square_feet}
              onChange={(e) => handleInputChange("square_feet", e.target.value)}
              onFocus={handleInputFocus}
              className="bg-input border-border"
              placeholder="Enter square footage"
              min="1000"
              max="1000000"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="meter" className="text-sm">
              Meter Type
            </Label>
            <Select
              value={String(formData.meter)}
              onValueChange={(value) => handleInputChange("meter", value)}
            >
              <SelectTrigger id="meter" className="bg-input border-border">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="0">Electricity</SelectItem>
                <SelectItem value="1">Chilled Water</SelectItem>
                <SelectItem value="2">Steam</SelectItem>
                <SelectItem value="3">Hot Water</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Environmental Conditions */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-foreground">
            Environmental Conditions
          </h3>

          <div className="space-y-2">
            <Label className="text-sm">
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
              className="w-full"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-sm">
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
              className="w-full"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-sm">
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
              className="w-full"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-sm">
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
              className="w-full"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-sm">
              Wind Speed: {formData.wind_speed.toFixed(1)} m/s
            </Label>
            <Slider
              value={[formData.wind_speed]}
              onValueChange={(value) => handleSliderChange("wind_speed", value)}
              min={0}
              max={30}
              step={0.1}
              className="w-full"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-sm">
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
              className="w-full"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-sm">
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
              className="w-full"
            />
          </div>
        </div>

        {/* Temporal Context */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-foreground">
            Temporal Context
          </h3>

          <div className="space-y-2">
            <Label htmlFor="date-picker" className="text-sm">
              Select Date
            </Label>
            <Input
              id="date-picker"
              type="date"
              value={formData.selectedDate.toISOString().split("T")[0]}
              onChange={handleDateChange}
              className="bg-input border-border"
            />
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="bg-muted p-3 rounded-md">
              <div className="text-muted-foreground">Day of Month</div>
              <div className="font-semibold text-lg">{formData.day}</div>
            </div>
            <div className="bg-muted p-3 rounded-md">
              <div className="text-muted-foreground">Month</div>
              <div className="font-semibold text-lg">{formData.month}</div>
            </div>
            <div className="bg-muted p-3 rounded-md">
              <div className="text-muted-foreground">Week of Year</div>
              <div className="font-semibold text-lg">{formData.week}</div>
            </div>
            <div className="bg-muted p-3 rounded-md">
              <div className="text-muted-foreground">Is Weekend</div>
              <div className="font-semibold text-lg">
                {formData.is_weekend ? "Yes" : "No"}
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <Label className="text-sm">Hour of Day: {formData.hour}</Label>
            <Slider
              value={[formData.hour]}
              onValueChange={(value) => handleSliderChange("hour", value)}
              min={0}
              max={23}
              step={1}
              className="w-full"
            />
          </div>
        </div>

        {/* Predict Button */}
        <Button
          onClick={handlePredict}
          disabled={isLoading}
          size="lg"
          className="w-full bg-emerald-600 hover:bg-emerald-700 text-white"
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
      </CardContent>
    </Card>
  );
}
