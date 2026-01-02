"use client";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
  Activity,
  ShieldCheck,
  RefreshCw,
  ExternalLink,
  Maximize2,
} from "lucide-react";
import { useState } from "react";

export default function MonitoringModal() {
  const [key, setKey] = useState(0);
  const handleRefresh = () => setKey((prev) => prev + 1);
  const handleOpenNewTab = () => window.open("/api/monitor", "_blank");

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          className="w-full justify-start gap-2 border-emerald-500/20 hover:bg-emerald-500/10 hover:text-emerald-600 hover:border-emerald-500/40 transition-all shadow-sm"
        >
          <Activity className="h-4 w-4 text-emerald-500" />
          <span className="font-medium">Model Health Dashboard</span>
          <Maximize2 className="h-3 w-3 ml-auto opacity-60" />
        </Button>
      </DialogTrigger>

      {/* Enhanced to 98vw and 95vh for maximum viewing space */}
      <DialogContent className="!max-w-[98vw] !w-[98vw] h-[95vh] flex flex-col p-0 gap-0 overflow-hidden border-2 border-emerald-500/20">
        <DialogHeader className="p-5 border-b bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-950/30 dark:to-teal-950/30">
          <div className="flex items-center justify-between">
            <div className="space-y-1.5">
              <DialogTitle className="flex items-center gap-2.5 text-xl">
                <div className="p-1.5 bg-emerald-500/10 rounded-lg">
                  <ShieldCheck className="h-5 w-5 text-emerald-600" />
                </div>
                <span className="bg-gradient-to-r from-emerald-700 to-teal-700 bg-clip-text text-transparent font-bold">
                  Evidently AI: Operational Monitoring
                </span>
              </DialogTitle>
              <DialogDescription className="text-sm pl-9">
                Real-time analysis of Data Drift, Target Drift, and Data Quality
                metrics
              </DialogDescription>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleOpenNewTab}
                className="gap-2 hover:bg-emerald-500/10 hover:text-emerald-600 hover:border-emerald-500/40 transition-all"
                title="Open in New Tab"
              >
                <ExternalLink className="h-4 w-4" />
                <span className="hidden sm:inline">New Tab</span>
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                className="gap-2 hover:bg-emerald-500/10 hover:text-emerald-600 hover:border-emerald-500/40 transition-all"
                title="Refresh Analysis"
              >
                <RefreshCw className="h-4 w-4" />
                <span className="hidden sm:inline">Refresh</span>
              </Button>
            </div>
          </div>
        </DialogHeader>

        <div className="flex-1 w-full h-full bg-white dark:bg-slate-950 relative">
          {/* Loading indicator overlay */}
          <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-emerald-50/50 to-teal-50/50 dark:from-emerald-950/20 dark:to-teal-950/20 pointer-events-none">
            <div className="flex flex-col items-center gap-3">
              <div className="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin" />
              <p className="text-sm text-muted-foreground font-medium">
                Loading dashboard...
              </p>
            </div>
          </div>

          <iframe
            key={key}
            src="/api/monitor"
            className="w-full h-full border-none relative z-10"
            title="Evidently AI Drift Report"
            onLoad={(e) => {
              // Hide loading indicator once iframe loads
              const parent = e.currentTarget.parentElement;
              if (parent) {
                const loader = parent.querySelector(".absolute");
                if (loader) (loader as HTMLElement).style.display = "none";
              }
            }}
          />
        </div>
      </DialogContent>
    </Dialog>
  );
}
