import { useCallback, useState } from "react";
import { Upload, X, Eye, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";

interface UploadSectionProps {
  onImageUpload: (file: File, imageUrl: string) => void;
  uploadedImage: string | null;
  isLoading: boolean;
  onReset: () => void;
}

export const UploadSection = ({ onImageUpload, uploadedImage, isLoading, onReset }: UploadSectionProps) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const { toast } = useToast();

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    handleFiles(files);
  }, []);

  const handleFiles = (files: File[]) => {
    const imageFile = files.find(file => file.type.startsWith('image/'));
    
    if (!imageFile) {
      toast({
        title: "Invalid file type",
        description: "Please select an image file (JPG, PNG, etc.)",
        variant: "destructive"
      });
      return;
    }

    if (imageFile.size > 10 * 1024 * 1024) { // 10MB limit
      toast({
        title: "File too large",
        description: "Please select an image smaller than 10MB",
        variant: "destructive"
      });
      return;
    }

    const imageUrl = URL.createObjectURL(imageFile);
    onImageUpload(imageFile, imageUrl);
    
    toast({
      title: "Image uploaded successfully",
      description: "AI analysis is starting...",
    });
  };

  return (
    <section id="upload" className="py-20 px-6">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-neon-cyan to-neon-purple bg-clip-text text-transparent">
            Upload Retinal Image
          </h2>
          <p className="text-muted-foreground text-lg">
            Select a clear retinal fundus image for AI analysis
          </p>
        </div>

        <Card className="relative overflow-hidden border-2 border-dashed border-border hover:border-neon-cyan/50 transition-all duration-300">
          <CardContent className="p-8">
            {!uploadedImage ? (
              <div
                className={`relative min-h-[300px] flex flex-col items-center justify-center text-center transition-all duration-300 ${
                  isDragOver ? 'bg-neon-cyan/5 border-neon-cyan' : ''
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <Upload className={`w-16 h-16 mb-4 ${isDragOver ? 'text-neon-cyan' : 'text-muted-foreground'} transition-colors`} />
                
                <h3 className="text-xl font-semibold mb-2">
                  Drag & drop your retinal image here
                </h3>
                
                <p className="text-muted-foreground mb-6">
                  or click to browse files
                </p>

                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />

                <Button className="bg-gradient-to-r from-neon-cyan to-neon-purple hover:shadow-neon">
                  <Upload className="w-4 h-4 mr-2" />
                  Select Image
                </Button>

                <p className="text-xs text-muted-foreground mt-4">
                  Supported formats: JPG, PNG, JPEG (Max 10MB)
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="relative">
                  <img
                    src={uploadedImage}
                    alt="Uploaded retinal scan"
                    className="w-full max-w-md mx-auto rounded-lg border border-neon-cyan/30 shadow-neon"
                  />
                  
                  {isLoading && (
                    <div className="absolute inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center rounded-lg">
                      <div className="text-center">
                        <Loader2 className="w-12 h-12 animate-spin text-neon-cyan mx-auto mb-4" />
                        <p className="text-lg font-semibold">Analyzing Image...</p>
                        <p className="text-sm text-muted-foreground">AI is processing your retinal scan</p>
                        
                        {/* Scanning line animation */}
                        <div className="relative mt-4 w-48 h-1 bg-muted rounded-full mx-auto overflow-hidden">
                          <div className="absolute top-0 left-0 h-full w-8 bg-gradient-to-r from-transparent via-neon-cyan to-transparent animate-scan-line"></div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex justify-center gap-4">
                  <Button
                    variant="outline"
                    onClick={onReset}
                    disabled={isLoading}
                    className="border-border hover:border-neon-cyan/50"
                  >
                    <X className="w-4 h-4 mr-2" />
                    Remove Image
                  </Button>
                  
                  <Button
                    disabled={isLoading}
                    className="bg-gradient-to-r from-neon-purple to-neon-pink hover:shadow-neon"
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    {isLoading ? 'Analyzing...' : 'Analyze Again'}
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </section>
  );
};