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
  const getGaugeMax = (value: number) => {
    if (value <= 100) return 100;
    if (value <= 500) return 500;
    if (value <= 1000) return 1000;
    if (value <= 2500) return 2500;
    if (value <= 5000) return 5000;
    return 10000;
  };

  const gaugeMax = prediction !== null ? getGaugeMax(prediction) : 5000;

  // Fix: Needle rotation should be from -90 (left) to +90 (right) degrees
  // Map prediction value (0 to gaugeMax) to angle (-90 to +90)
  const normalizedValue =
    prediction !== null ? -90 + (prediction / gaugeMax) * 180 : -90;

  // Arc progress for the colored arc (0 to 235 path units)
  const arcProgress =
    prediction !== null ? Math.min((prediction / gaugeMax) * 235, 235) : 0;

  return (
    <Card className="bg-card border-border flex flex-col items-center justify-center">
      <CardHeader className="text-center w-full">
        <CardTitle className="text-lg font-light text-foreground">
          Prediction Gauge
        </CardTitle>
        <CardDescription className="text-muted-foreground">
          Estimated meter reading
        </CardDescription>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col items-center justify-center w-full py-8">
        {isLoading ? (
          <div className="flex flex-col items-center gap-4">
            <div className="relative w-32 h-32">
              <div className="absolute inset-0 rounded-full border-8 border-border border-t-[#ea580c] animate-spin" />
            </div>
            <p className="text-muted-foreground text-sm">
              Processing prediction...
            </p>
          </div>
        ) : prediction !== null ? (
          <div className="flex flex-col items-center gap-4">
            <div className="relative w-40 h-40 flex items-center justify-center">
              <svg className="w-full h-full" viewBox="0 0 200 200">
                {/* Gauge background circle */}
                <circle
                  cx="100"
                  cy="100"
                  r="90"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  className="text-border"
                />
                {/* Gauge arc background (semi-circle from left to right) */}
                <path
                  d="M 25 100 A 75 75 0 0 1 175 100"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="8"
                  className="text-border"
                />
                {/* Colored arc based on prediction */}
                <path
                  d="M 25 100 A 75 75 0 0 1 175 100"
                  fill="none"
                  stroke="#ea580c"
                  strokeWidth="8"
                  strokeDasharray={`${arcProgress} 235`}
                  strokeLinecap="round"
                />
                {/* Needle - now properly rotates from left (-90°) to right (+90°) */}
                <g transform={`rotate(${normalizedValue} 100 100)`}>
                  <line
                    x1="100"
                    y1="100"
                    x2="100"
                    y2="30"
                    stroke="#ea580c"
                    strokeWidth="3"
                    strokeLinecap="round"
                  />
                  <circle cx="100" cy="100" r="5" fill="#ea580c" />
                </g>
                {/* Labels */}
                <text
                  x="25"
                  y="115"
                  textAnchor="middle"
                  className="text-xs fill-muted-foreground"
                >
                  0
                </text>
                <text
                  x="100"
                  y="25"
                  textAnchor="middle"
                  className="text-xs fill-muted-foreground"
                >
                  {(gaugeMax / 2).toLocaleString()}
                </text>
                <text
                  x="175"
                  y="115"
                  textAnchor="middle"
                  className="text-xs fill-muted-foreground"
                >
                  {gaugeMax.toLocaleString()}
                </text>
              </svg>
            </div>
            <div className="text-center">
              <p className="text-4xl font-light text-[#ea580c]">
                {prediction.toFixed(2)}
              </p>
              <p className="text-muted-foreground text-sm mt-1">kWh</p>
            </div>
          </div>
        ) : (
          <div className="text-center">
            <div className="relative w-32 h-32 mx-auto mb-4 opacity-30">
              <svg className="w-full h-full" viewBox="0 0 200 200">
                <circle
                  cx="100"
                  cy="100"
                  r="90"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  className="text-border"
                />
                <path
                  d="M 25 100 A 75 75 0 0 1 175 100"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="8"
                  className="text-border"
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
