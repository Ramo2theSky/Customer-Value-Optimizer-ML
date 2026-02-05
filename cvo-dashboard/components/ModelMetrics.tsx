"use client";

import { CheckCircle2, AlertCircle, Brain, TrendingUp, BarChart3 } from "lucide-react";

interface FeatureImportance {
  feature: string;
  importance: number;
}

interface ConfusionMatrix {
  truePositive: number;
  falsePositive: number;
  trueNegative: number;
  falseNegative: number;
}

interface ModelMetricsProps {
  performance: {
    accuracy: number;
    precision: number;
    recall: number;
    f1Score: number;
    aucRoc: number;
    trainingSamples: number;
    testSamples: number;
    lastTrainingDate: string;
    modelVersion: string;
    featureImportance: FeatureImportance[];
    confusionMatrix: ConfusionMatrix;
  };
}

export default function ModelMetrics({ performance }: ModelMetricsProps) {
  const metrics = [
    { label: "Akurasi", value: performance.accuracy, icon: <CheckCircle2 className="w-4 h-4" /> },
    { label: "Presisi", value: performance.precision, icon: <BarChart3 className="w-4 h-4" /> },
    { label: "Recall", value: performance.recall, icon: <TrendingUp className="w-4 h-4" /> },
    { label: "F1 Score", value: performance.f1Score, icon: <Brain className="w-4 h-4" /> },
    { label: "AUC-ROC", value: performance.aucRoc * 100, icon: <AlertCircle className="w-4 h-4" /> },
  ];

  const totalPredictions =
    performance.confusionMatrix.truePositive +
    performance.confusionMatrix.falsePositive +
    performance.confusionMatrix.trueNegative +
    performance.confusionMatrix.falseNegative;

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Performa Model</h3>
          <p className="text-sm text-gray-500">
            Versi {performance.modelVersion} • Dilatih pada {new Date(performance.lastTrainingDate).toLocaleDateString()}
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 bg-green-100 rounded-full">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span className="text-xs font-medium text-green-700">Aktif</span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        {metrics.map((metric) => (
          <div
            key={metric.label}
            className="text-center p-4 rounded-lg bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-200"
          >
            <div className="flex justify-center mb-2 text-pln-blue">{metric.icon}</div>
            <div className="text-2xl font-bold text-gray-900">
              {metric.value.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500">{metric.label}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-4">Matriks Confusion</h4>
          <div className="grid grid-cols-2 gap-2">
            <div className="p-3 bg-green-50 rounded-lg border border-green-200">
              <div className="text-xs text-gray-600 mb-1">True Positive</div>
              <div className="text-lg font-bold text-green-700">
                {performance.confusionMatrix.truePositive.toLocaleString()}
              </div>
              <div className="text-xs text-green-600">
                {((performance.confusionMatrix.truePositive / totalPredictions) * 100).toFixed(1)}%
              </div>
            </div>
            <div className="p-3 bg-red-50 rounded-lg border border-red-200">
              <div className="text-xs text-gray-600 mb-1">False Positive</div>
              <div className="text-lg font-bold text-red-700">
                {performance.confusionMatrix.falsePositive.toLocaleString()}
              </div>
              <div className="text-xs text-red-600">
                {((performance.confusionMatrix.falsePositive / totalPredictions) * 100).toFixed(1)}%
              </div>
            </div>
            <div className="p-3 bg-red-50 rounded-lg border border-red-200">
              <div className="text-xs text-gray-600 mb-1">False Negative</div>
              <div className="text-lg font-bold text-red-700">
                {performance.confusionMatrix.falseNegative.toLocaleString()}
              </div>
              <div className="text-xs text-red-600">
                {((performance.confusionMatrix.falseNegative / totalPredictions) * 100).toFixed(1)}%
              </div>
            </div>
            <div className="p-3 bg-green-50 rounded-lg border border-green-200">
              <div className="text-xs text-gray-600 mb-1">True Negative</div>
              <div className="text-lg font-bold text-green-700">
                {performance.confusionMatrix.trueNegative.toLocaleString()}
              </div>
              <div className="text-xs text-green-600">
                {((performance.confusionMatrix.trueNegative / totalPredictions) * 100).toFixed(1)}%
              </div>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-gray-100">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Sampel Pelatihan</span>
              <span className="font-medium text-gray-900">
                {performance.trainingSamples.toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between text-sm mt-2">
              <span className="text-gray-500">Sampel Pengujian</span>
              <span className="font-medium text-gray-900">
                {performance.testSamples.toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-4">Tingkat Kepentingan Fitur</h4>
          <div className="space-y-3">
            {performance.featureImportance.slice(0, 5).map((feature, index) => (
              <div key={feature.feature}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">{feature.feature}</span>
                  <span className="font-medium text-gray-900">
                    {(feature.importance * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-1000"
                    style={{
                      width: `${feature.importance * 100}%`,
                      backgroundColor: index === 0 ? "#0047AB" : index === 1 ? "#0066CC" : "#0099FF",
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
