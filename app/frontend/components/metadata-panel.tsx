"use client";

import { useState, useEffect } from "react";
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
import { AlertCircle } from "lucide-react";

interface MetadataPanelProps {
  recentPredictions: Array<{ value: number; timestamp: Date }>;
}

export default function MetadataPanel({
  recentPredictions,
}: MetadataPanelProps) {
  const [metadata, setMetadata] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchMetadata() {
      try {
        const res = await fetch("/api/metadata");
        const data = await res.json();
        setMetadata(data);
      } catch {
        setMetadata({ status: "offline" });
      } finally {
        setLoading(false);
      }
    }
    fetchMetadata();
  }, []);

  const chartData = recentPredictions
    .slice(0, 5)
    .reverse()
    .map((pred, idx) => ({
      name: `P${idx + 1}`,
      value: pred.value / 1000,
      originalValue: pred.value,
    }));

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-lg font-light text-foreground">
          Model Metadata
        </CardTitle>
        <CardDescription className="text-muted-foreground">
          System information & recent predictions
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-[#ea580c]">
            Model Information
          </h3>

          {loading ? (
            <div className="h-32 bg-muted/20 animate-pulse rounded-lg border border-border" />
          ) : metadata?.status === "offline" ? (
            /* SERVER DOWN STATE */
            <div className="bg-red-500/10 rounded-lg p-6 border border-red-500/50 flex flex-col items-center justify-center text-center">
              <AlertCircle className="text-red-500 mb-2" size={20} />
              <p className="text-xs font-semibold text-red-500 uppercase">
                Server Offline
              </p>
              <p className="text-[10px] text-red-400 mt-1">
                Check MLflow & Backend Status
              </p>
            </div>
          ) : (
            /* LIVE DATA */
            <div className="bg-muted/50 rounded-lg p-4 space-y-2 border border-border">
              <div className="flex justify-between">
                <span className="text-xs text-muted-foreground">
                  Model Version
                </span>
                <span className="text-sm text-foreground">
                  {metadata?.version}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-muted-foreground">RMSE</span>
                <span className="text-sm text-foreground">
                  {metadata?.rmse}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-muted-foreground">
                  Last Updated
                </span>
                <span className="text-sm text-foreground">
                  {new Date(metadata?.last_updated).toLocaleDateString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-muted-foreground">Accuracy</span>
                <span className="text-sm text-[#ea580c] font-medium">
                  {metadata?.accuracy}
                </span>
              </div>
            </div>
          )}

          <MonitoringModal />
        </div>

        <div className="space-y-3">
          <h3 className="text-sm font-medium text-[#ea580c]">
            Recent Predictions
          </h3>
          {chartData.length > 0 ? (
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="currentColor"
                    className="text-border"
                  />
                  <XAxis
                    dataKey="name"
                    tick={{
                      fill: "currentColor",
                      fontSize: 12,
                    }}
                    className="text-muted-foreground"
                  />
                  <YAxis
                    tick={{
                      fill: "currentColor",
                      fontSize: 12,
                    }}
                    className="text-muted-foreground"
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "var(--color-card)",
                      border: "1px solid var(--color-border)",
                      borderRadius: "6px",
                      color: "var(--color-foreground)",
                    }}
                    formatter={(value, name, props) => {
                      // Use the original value from the data item
                      const originalValue = props.payload.originalValue;
                      return [`${originalValue.toFixed(2)} kWh`, "Prediction"];
                    }}
                    labelFormatter={(label) => `Prediction ${label}`}
                  />
                  <Bar
                    dataKey="value"
                    fill="#ea580c"
                    radius={[4, 4, 0, 0]}
                    name="Energy Usage"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center bg-muted/50 rounded-lg border border-border">
              <p className="text-sm text-muted-foreground">
                No predictions yet
              </p>
            </div>
          )}
        </div>

        {/* Comparison Stats */}
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-[#ea580c]">Typical Usage</h3>
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-muted/50 rounded p-3 border border-border">
              <p className="text-xs text-muted-foreground">Low</p>
              <p className="text-sm font-medium text-foreground">45k kWh</p>
            </div>
            <div className="bg-muted/50 rounded p-3 border border-border">
              <p className="text-xs text-muted-foreground">Peak</p>
              <p className="text-sm font-medium text-foreground">180k kWh</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
