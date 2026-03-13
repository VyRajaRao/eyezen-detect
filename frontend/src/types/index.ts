export type PredictionResult = {
  disease: string;
  confidence: number;
  heatmap?: string;
};