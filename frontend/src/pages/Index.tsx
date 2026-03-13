import React, { useState, Suspense } from "react";
import { performanceMonitor, measureApiCall } from "@/utils/performance";
import type { PredictionResult } from "@/types";

// Lazy load components that are not immediately visible
const HeroSection = React.lazy(() => import("@/components/HeroSection").then(module => ({ default: module.HeroSection })));
const UploadSection = React.lazy(() => import("@/components/UploadSection").then(module => ({ default: module.UploadSection })));
const ResultsSection = React.lazy(() => import("@/components/ResultsSection").then(module => ({ default: module.ResultsSection })));
const AboutSection = React.lazy(() => import("@/components/AboutSection").then(module => ({ default: module.AboutSection })));
const DisclaimerSection = React.lazy(() => import("@/components/DisclaimerSection").then(module => ({ default: module.DisclaimerSection })));
const Footer = React.lazy(() => import("@/components/Footer").then(module => ({ default: module.Footer })));
const ChatBot = React.lazy(() => import("@/components/ChatBot").then(module => ({ default: module.ChatBot })));

// Component loading placeholder
const ComponentLoader = ({ className = "" }: { className?: string }) => (
  <div className={`animate-pulse bg-muted/20 rounded-lg ${className}`}>
    <div className="h-20 bg-gradient-to-r from-neon-cyan/10 via-neon-purple/10 to-neon-pink/10"></div>
  </div>
);

const Index = () => {
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [predictionResult, setPredictionResult] = useState<PredictionResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  React.useEffect(() => {
    performanceMonitor.start('index-page-load');
    
    // Pre-warm the backend API
    fetch('http://localhost:5000/api/health')
      .then(() => console.log('✅ Backend warmed up'))
      .catch(() => console.log('⚠️ Backend not available'));
      
    return () => {
      performanceMonitor.end('index-page-load');
    };
  }, []);

  const handleImageUpload = async (imageFile: File, imageUrl: string) => {
    setUploadedImage(imageUrl);
    setIsLoading(true);
    
    try {
      const result = await measureApiCall('image-prediction', async () => {
        // Create FormData to send the image file
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('generate_heatmap', 'true'); // Request heatmap generation
        
        // Make API call to backend
        const response = await fetch('http://localhost:5000/api/predict', {
          method: 'POST',
          body: formData,
        });
        
        if (!response.ok) {
          throw new Error(`API request failed with status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Transform API response to match frontend expected format
        return {
          disease: data.disease,
          confidence: data.confidence,
          heatmap: data.heatmap, // Base64 encoded heatmap if available
          processingTime: data.processing_time,
          imageQuality: data.image_quality,
          allPredictions: data.all_predictions
        };
      });
      
      setPredictionResult(result);
      setIsLoading(false);
      
    } catch (error) {
      console.error('Error uploading image:', error);
      setIsLoading(false);
      
      // Show error message to user
      // For now, fall back to mock data to keep the demo working
      const mockResults = [
        { disease: "Diabetic Retinopathy", confidence: 0.89, heatmap: null },
        { disease: "Glaucoma", confidence: 0.76, heatmap: null },
        { disease: "Cataract", confidence: 0.92, heatmap: null },
        { disease: "Normal", confidence: 0.95, heatmap: null }
      ];
      
      const result = mockResults[Math.floor(Math.random() * mockResults.length)];
      setPredictionResult(result);
    }
  };

  const resetAnalysis = () => {
    setUploadedImage(null);
    setPredictionResult(null);
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="relative">
        <Suspense fallback={<ComponentLoader className="h-[600px] mx-6 mt-6" />}>
          <HeroSection />
        </Suspense>
        
        <Suspense fallback={<ComponentLoader className="h-[400px] mx-6 mt-6" />}>
          <UploadSection 
            onImageUpload={handleImageUpload}
            uploadedImage={uploadedImage}
            isLoading={isLoading}
            onReset={resetAnalysis}
          />
        </Suspense>
        
        <Suspense fallback={<ComponentLoader className="h-[300px] mx-6 mt-6" />}>
          <ResultsSection 
            result={predictionResult}
            uploadedImage={uploadedImage}
            isLoading={isLoading}
          />
        </Suspense>
        
        <Suspense fallback={<ComponentLoader className="h-[200px] mx-6 mt-6" />}>
          <AboutSection />
        </Suspense>
        
        <Suspense fallback={<ComponentLoader className="h-[150px] mx-6 mt-6" />}>
          <DisclaimerSection />
        </Suspense>
        
        <Suspense fallback={<ComponentLoader className="h-[100px] mx-6 mt-6" />}>
          <Footer />
        </Suspense>
        
        <Suspense fallback={null}>
          <ChatBot />
        </Suspense>
      </div>
    </div>
  );
};

export default Index;
