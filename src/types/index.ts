export type ODIRPrediction = {
  label: string;
  score: number;
};

export type PredictionResult = {
  disease: string;
  confidence: number;
  heatmap?: string;
  // Extended fields from the ML service
  is_retinal?: boolean;
  odir_predictions?: ODIRPrediction[];
  aptos_dr_grade?: string | null;
  model_version?: string | null;
  notes?: string | null;
  /** True when the Python ML service is unavailable and placeholder data is shown. */
  demo_mode?: boolean;
};