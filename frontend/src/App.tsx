import React, { Suspense } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { performanceMonitor } from "@/utils/performance";

// Lazy load components for better performance
const Index = React.lazy(() => import("./pages/Index"));
const NotFound = React.lazy(() => import("./pages/NotFound"));

// Configure React Query with performance optimizations
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Loading spinner component
const LoadingSpinner = () => (
  <div className="min-h-screen bg-background flex items-center justify-center">
    <div className="relative w-16 h-16">
      <div className="absolute inset-0 border-4 border-neon-cyan/20 rounded-full animate-spin"></div>
      <div className="absolute inset-2 border-4 border-neon-purple/30 border-t-transparent rounded-full animate-spin"></div>
      <div className="absolute inset-4 border-2 border-neon-pink/40 border-t-transparent rounded-full animate-spin"></div>
    </div>
  </div>
);

const App = () => {
  React.useEffect(() => {
    // Start performance monitoring
    performanceMonitor.start('app-initialization');
    
    // Log performance report after initial load
    const timer = setTimeout(() => {
      performanceMonitor.end('app-initialization');
      performanceMonitor.logPerformanceReport();
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Suspense fallback={<LoadingSpinner />}>
            <Routes>
              <Route path="/" element={<Index />} />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
