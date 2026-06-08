interface Step {
  id: number;
  name: string;
}

interface StepWizardProps {
  steps: Step[];
  currentStep: number;
  onStepClick?: (step: number) => void;
}

export default function StepWizard({ steps, currentStep, onStepClick }: StepWizardProps) {
  return (
    <div className="flex items-center justify-center mb-6">
      {steps.map((step, index) => (
        <div key={step.id} className="flex items-center">
          <button
            onClick={() => onStepClick?.(step.id)}
            disabled={step.id > currentStep}
            className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
              step.id === currentStep
                ? 'bg-blue-600 text-white'
                : step.id < currentStep
                ? 'bg-green-500 text-white cursor-pointer hover:bg-green-600'
                : 'bg-gray-200 text-gray-500'
            }`}
          >
            {step.id < currentStep ? '✓' : step.id}
          </button>
          <span className={`ml-2 text-sm ${
            step.id === currentStep ? 'text-gray-900 font-medium' : 'text-gray-500'
          }`}>
            {step.name}
          </span>
          {index < steps.length - 1 && (
            <div className={`w-16 h-0.5 mx-4 ${
              step.id < currentStep ? 'bg-green-500' : 'bg-gray-200'
            }`} />
          )}
        </div>
      ))}
    </div>
  );
}