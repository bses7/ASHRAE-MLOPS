"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import InputPanel from "@/components/input-panel"
import PredictionDisplay from "@/components/prediction-display"
import MetadataPanel from "@/components/metadata-panel"

export default function Dashboard() {
  const [isLoading, setIsLoading] = useState(false)
  const [healthStatus, setHealthStatus] = useState<"online" | "offline">("offline")
  const [prediction, setPrediction] = useState<number | null>(null)
  const [recentPredictions, setRecentPredictions] = useState<Array<{ value: number; timestamp: Date }>>([])

  // Check backend health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch("/api/health")
        if (res.ok) {
          setHealthStatus("online")
        } else {
          setHealthStatus("offline")
        }
      } catch {
        setHealthStatus("offline")
      }
    }

    checkHealth()
  }, [])

  const handlePredict = async (inputs: any) => {
    setIsLoading(true)
    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(inputs),
      })

      if (res.ok) {
        const data = await res.json()
        const predictedValue = data.meter_reading
        setPrediction(predictedValue)
        setRecentPredictions((prev) => [{ value: predictedValue, timestamp: new Date() }, ...prev.slice(0, 9)])
      }
    } catch (error) {
      console.error("Prediction error:", error)
    } finally {
      setIsLoading(false)
    }
  }

  if (healthStatus === "offline") {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <Card className="max-w-md border-destructive/50 bg-destructive/5">
          <CardHeader>
            <CardTitle className="text-destructive">Engine Offline</CardTitle>
            <CardDescription>The prediction engine is currently unavailable</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Please ensure the FastAPI backend is running at http://localhost:8000
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Energy Prediction Control Room</h1>
              <p className="text-muted-foreground mt-1">Real-time building energy forecasting</p>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-accent rounded-lg">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-sm font-medium text-foreground">System Active</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Input Panel */}
          <InputPanel onPredict={handlePredict} isLoading={isLoading} />

          {/* Center Column - Prediction Display */}
          <PredictionDisplay prediction={prediction} isLoading={isLoading} />

          {/* Right Column - Metadata Panel */}
          <MetadataPanel recentPredictions={recentPredictions} />
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-card mt-12">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>© 2025 Energy Prediction System</span>
            <a
              href="http://localhost:5000"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              View Model Lineage in MLflow →
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}
