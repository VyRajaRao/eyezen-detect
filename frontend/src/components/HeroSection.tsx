import { Eye, Brain, Zap } from "lucide-react";

export const HeroSection = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated background grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,hsl(var(--border))_1px,transparent_1px),linear-gradient(to_bottom,hsl(var(--border))_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-20 animate-pulse" />
      
      {/* Neon glow orbs */}
      <div className="absolute top-20 left-20 w-32 h-32 bg-neon-cyan/20 rounded-full blur-3xl animate-pulse-neon" />
      <div className="absolute bottom-40 right-20 w-40 h-40 bg-neon-purple/20 rounded-full blur-3xl animate-pulse-neon" style={{ animationDelay: '1s' }} />
      <div className="absolute top-1/3 right-1/4 w-24 h-24 bg-neon-pink/20 rounded-full blur-2xl animate-pulse-neon" style={{ animationDelay: '2s' }} />
      
      <div className="relative z-10 text-center max-w-4xl mx-auto px-6">
        <div className="flex items-center justify-center gap-4 mb-6">
          <Eye className="w-12 h-12 text-neon-cyan animate-pulse-neon" />
          <Brain className="w-10 h-10 text-neon-purple animate-pulse-neon" style={{ animationDelay: '0.5s' }} />
          <Zap className="w-8 h-8 text-neon-pink animate-pulse-neon" style={{ animationDelay: '1s' }} />
        </div>
        
        <h1 className="text-6xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-neon-cyan via-neon-purple to-neon-pink bg-clip-text text-transparent animate-fade-in-up">
          AI EyeScan
        </h1>
        
        <p className="text-xl md:text-2xl text-muted-foreground mb-4 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          Advanced Eye Disease Detection Powered by AI
        </p>
        
        <p className="text-lg text-muted-foreground/80 mb-8 max-w-2xl mx-auto animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
          Upload a retinal fundus image and get instant AI-powered analysis for diabetic retinopathy, glaucoma, cataracts, and more.
        </p>
        
        <div className="flex flex-wrap justify-center gap-4 text-sm text-muted-foreground animate-fade-in-up" style={{ animationDelay: '0.6s' }}>
          <div className="flex items-center gap-2 bg-card/50 backdrop-blur-sm px-4 py-2 rounded-full border border-neon-cyan/20">
            <div className="w-2 h-2 bg-neon-cyan rounded-full animate-pulse" />
            89% Accuracy
          </div>
          <div className="flex items-center gap-2 bg-card/50 backdrop-blur-sm px-4 py-2 rounded-full border border-neon-purple/20">
            <div className="w-2 h-2 bg-neon-purple rounded-full animate-pulse" />
            Instant Results
          </div>
          <div className="flex items-center gap-2 bg-card/50 backdrop-blur-sm px-4 py-2 rounded-full border border-neon-pink/20">
            <div className="w-2 h-2 bg-neon-pink rounded-full animate-pulse" />
            Free Analysis
          </div>
        </div>
      </div>
      
      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 border-2 border-neon-cyan/50 rounded-full flex justify-center">
          <div className="w-1 h-3 bg-neon-cyan rounded-full mt-2 animate-pulse" />
        </div>
      </div>
    </section>
  );
};