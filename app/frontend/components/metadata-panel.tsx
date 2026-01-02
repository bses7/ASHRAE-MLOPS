"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import MonitoringModal from "@/components/MonitorModal";

interface MetadataPanelProps {
  recentPredictions: Array<{ value: number; timestamp: Date }>;
}

export default function MetadataPanel({
  recentPredictions,
}: MetadataPanelProps) {
  const chartData = recentPredictions
    .slice(0, 5)
    .reverse()
    .map((pred, idx) => ({
      name: `P${idx + 1}`,
      value: pred.value / 1000,
    }));

  return (
    <Card className="lg:col-span-1 border-border bg-card">
      <CardHeader>
        <CardTitle className="text-lg">Model Metadata</CardTitle>
        <CardDescription>
          System information & recent predictions
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-foreground">
            Model Information
          </h3>
          <div className="bg-accent rounded-lg p-4 space-y-2">
            <div className="flex justify-between">
              <span className="text-xs text-muted-foreground">
                Model Version
              </span>
              <span className="text-sm font-medium text-foreground">
                v2.1.0
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-muted-foreground">RMSE</span>
              <span className="text-sm font-medium text-foreground">
                12.4 kWh
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-muted-foreground">
                Last Updated
              </span>
              <span className="text-sm font-medium text-foreground">
                Dec 25, 2025
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-muted-foreground">Accuracy</span>
              <span className="text-sm font-medium text-emerald-600">
                94.2%
              </span>
            </div>
          </div>

          <MonitoringModal />
        </div>

        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-foreground">
            Recent Predictions
          </h3>
          {chartData.length > 0 ? (
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="hsl(var(--color-border))"
                  />
                  <XAxis
                    dataKey="name"
                    tick={{
                      fill: "hsl(var(--color-muted-foreground))",
                      fontSize: 12,
                    }}
                  />
                  <YAxis
                    tick={{
                      fill: "hsl(var(--color-muted-foreground))",
                      fontSize: 12,
                    }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--color-card))",
                      border: "1px solid hsl(var(--color-border))",
                      borderRadius: "6px",
                    }}
                    formatter={(value) =>
                      typeof value === "number"
                        ? `${value.toFixed(1)}k kWh`
                        : `${value} kWh`
                    }
                  />
                  <Bar
                    dataKey="value"
                    fill="hsl(from var(--color-chart-1) h s l)"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center bg-accent rounded-lg">
              <p className="text-sm text-muted-foreground">
                No predictions yet
              </p>
            </div>
          )}
        </div>

        {/* Comparison Stats */}
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-foreground">
            Typical Usage
          </h3>
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-accent rounded p-3">
              <p className="text-xs text-muted-foreground">Low</p>
              <p className="text-sm font-bold text-foreground">45k kWh</p>
            </div>
            <div className="bg-accent rounded p-3">
              <p className="text-xs text-muted-foreground">Peak</p>
              <p className="text-sm font-bold text-foreground">180k kWh</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
