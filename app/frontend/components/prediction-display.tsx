"use client";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface PredictionDisplayProps {
  prediction: number | null;
  isLoading: boolean;
}

export default function PredictionDisplay({
  prediction,
  isLoading,
}: PredictionDisplayProps) {
  // For per-day kWh, typical range is 0-10,000 kWh
  // But we'll make it dynamic based on actual prediction
  const getGaugeMax = (value: number) => {
    if (value <= 100) return 100;
    if (value <= 500) return 500;
    if (value <= 1000) return 1000;
    if (value <= 2500) return 2500;
    if (value <= 5000) return 5000;
    return 10000;
  };

  const gaugeMax = prediction !== null ? getGaugeMax(prediction) : 5000;
  const normalizedValue =
    prediction !== null ? Math.min((prediction / gaugeMax) * 180, 180) : 0;
  const arcProgress =
    prediction !== null ? Math.min((prediction / gaugeMax) * 235, 235) : 0;

  return (
    <Card className="lg:col-span-1 border-border bg-card flex flex-col items-center justify-center">
      <CardHeader className="text-center w-full">
        <CardTitle className="text-lg">Prediction Gauge</CardTitle>
        <CardDescription>Estimated meter reading</CardDescription>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col items-center justify-center w-full">
        {isLoading ? (
          <div className="flex flex-col items-center gap-4">
            <div className="relative w-32 h-32">
              <div className="absolute inset-0 rounded-full border-8 border-border border-t-emerald-500 animate-spin" />
            </div>
            <p className="text-muted-foreground text-sm">
              Processing prediction...
            </p>
          </div>
        ) : prediction !== null ? (
          <div className="flex flex-col items-center gap-4">
            <div className="relative w-40 h-40 flex items-center justify-center">
              <svg className="w-full h-full" viewBox="0 0 200 200">
                {/* Gauge background */}
                <circle
                  cx="100"
                  cy="100"
                  r="90"
                  fill="none"
                  stroke="hsl(var(--border))"
                  strokeWidth="2"
                />
                {/* Gauge arc (0-100%) */}
                <path
                  d="M 25 100 A 75 75 0 0 1 175 100"
                  fill="none"
                  stroke="hsl(var(--border))"
                  strokeWidth="8"
                />
                {/* Colored arc based on prediction */}
                <path
                  d="M 25 100 A 75 75 0 0 1 175 100"
                  fill="none"
                  stroke="#10b981"
                  strokeWidth="8"
                  strokeDasharray={`${Math.min(arcProgress, 235)} 235`}
                />
                {/* Needle */}
                <g transform={`rotate(${normalizedValue} 100 100)`}>
                  <line
                    x1="100"
                    y1="100"
                    x2="100"
                    y2="30"
                    stroke="hsl(var(--foreground))"
                    strokeWidth="3"
                  />
                  <circle
                    cx="100"
                    cy="100"
                    r="5"
                    fill="hsl(var(--foreground))"
                  />
                </g>
                {/* Labels */}
                <text
                  x="100"
                  y="160"
                  textAnchor="middle"
                  className="text-xs fill-muted-foreground"
                >
                  0
                </text>
                <text
                  x="165"
                  y="105"
                  textAnchor="middle"
                  className="text-xs fill-muted-foreground"
                >
                  {(gaugeMax / 2).toLocaleString()}
                </text>
                <text
                  x="100"
                  y="25"
                  textAnchor="middle"
                  className="text-xs fill-muted-foreground"
                >
                  {gaugeMax.toLocaleString()}
                </text>
              </svg>
            </div>
            <div className="text-center">
              <p className="text-4xl font-bold text-emerald-600">
                {prediction.toFixed(2)}
              </p>
              <p className="text-muted-foreground text-sm mt-1">kWh per day</p>
            </div>
          </div>
        ) : (
          <div className="text-center">
            <div className="relative w-32 h-32 mx-auto mb-4 opacity-50">
              <svg className="w-full h-full" viewBox="0 0 200 200">
                <circle
                  cx="100"
                  cy="100"
                  r="90"
                  fill="none"
                  stroke="hsl(var(--border))"
                  strokeWidth="2"
                />
                <path
                  d="M 25 100 A 75 75 0 0 1 175 100"
                  fill="none"
                  stroke="hsl(var(--border))"
                  strokeWidth="8"
                />
              </svg>
            </div>
            <p className="text-muted-foreground text-sm">
              Configure inputs and click Predict
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
