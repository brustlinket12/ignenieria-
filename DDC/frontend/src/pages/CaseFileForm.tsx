import { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import StepWizard from '../components/StepWizard';
import type { RiskProfileForm } from '../schemas/caseFile';

const clientSchema = z.object({
  client_name: z.string().min(2, 'Nombre requerido'),
  client_id_type: z.string().min(1, 'Tipo de ID requerido'),
  client_id_number: z.string().min(1, 'Numero de ID requerido'),
  client_country: z.string().min(1, 'Pais requerido'),
});

const riskSchema = z.object({
  sector_score: z.number().min(0).max(30),
  jurisdiction_score: z.number().min(0).max(20),
  pep_score: z.number().min(0).max(20),
  volume_score: z.number().min(0).max(20),
  funds_origin_score: z.number().min(0).max(10),
});

type ClientForm = z.infer<typeof clientSchema>;
type RiskForm = z.infer<typeof riskSchema>;

const ID_TYPES = ['DNI', 'PASAPORTE', 'CEDULA'];
const COUNTRIES = ['Argentina', 'Brasil', 'Chile', 'Uruguay', 'Paraguay', 'Colombia', 'Peru', 'Mexico'];

export default function CaseFileForm() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [caseFileId, setCaseFileId] = useState<number | null>(null);
  const [riskResult, setRiskResult] = useState<any>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const clientForm = useForm<ClientForm>({
    resolver: zodResolver(clientSchema),
    defaultValues: {
      client_name: '',
      client_id_type: '',
      client_id_number: '',
      client_country: '',
    },
  });

  const riskForm = useForm<RiskForm>({
    resolver: zodResolver(riskSchema),
    defaultValues: {
      sector_score: 0,
      jurisdiction_score: 0,
      pep_score: 0,
      volume_score: 0,
      funds_origin_score: 0,
    },
  });

  const steps = [
    { id: 1, name: 'Datos del Cliente' },
    { id: 2, name: 'Perfil de Riesgo' },
    { id: 3, name: 'Documentos' },
    { id: 4, name: 'Revision y Envio' },
  ];

  const handleClientSubmit = async (data: ClientForm) => {
    try {
      setIsSubmitting(true);
      const response = await api.post('/case-files', data);
      setCaseFileId(response.data.id);
      setStep(2);
    } catch (error) {
      console.error('Error creando expediente:', error);
      alert('Error al crear el expediente');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRiskSubmit = async (data: RiskForm) => {
    if (!caseFileId) return;

    try {
      setIsSubmitting(true);
      const response = await api.post(`/case-files/${caseFileId}/risk-assessment`, data);
      setRiskResult(response.data);
      setStep(3);
    } catch (error) {
      console.error('Error calculando riesgo:', error);
      alert('Error al calcular el riesgo');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmit = async () => {
    if (!caseFileId) return;

    try {
      setIsSubmitting(true);
      await api.post(`/case-files/${caseFileId}/submit`);
      navigate('/case-files');
    } catch (error: any) {
      alert(error.response?.data?.error || 'Error al enviar expediente');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Nuevo Expediente</h1>

      <StepWizard steps={steps} currentStep={step} onStepClick={(s) => s < step && setStep(s)} />

      <div className="bg-white rounded-lg shadow p-6 mt-6">
        {step === 1 && (
          <form onSubmit={clientForm.handleSubmit(handleClientSubmit)} className="space-y-4">
            <h2 className="text-lg font-semibold">Datos del Cliente</h2>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nombre Completo</label>
              <input
                {...clientForm.register('client_name')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="Nombre del cliente"
              />
              {clientForm.formState.errors.client_name && (
                <p className="text-red-500 text-sm">{clientForm.formState.errors.client_name.message}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Documento</label>
                <select
                  {...clientForm.register('client_id_type')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="">Seleccionar...</option>
                  {ID_TYPES.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
                {clientForm.formState.errors.client_id_type && (
                  <p className="text-red-500 text-sm">{clientForm.formState.errors.client_id_type.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Numero de Documento</label>
                <input
                  {...clientForm.register('client_id_number')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="12345678"
                />
                {clientForm.formState.errors.client_id_number && (
                  <p className="text-red-500 text-sm">{clientForm.formState.errors.client_id_number.message}</p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Pais</label>
              <select
                {...clientForm.register('client_country')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="">Seleccionar...</option>
                {COUNTRIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
              {clientForm.formState.errors.client_country && (
                <p className="text-red-500 text-sm">{clientForm.formState.errors.client_country.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {isSubmitting ? 'Guardando...' : 'Continuar'}
            </button>
          </form>
        )}

        {step === 2 && (
          <form onSubmit={riskForm.handleSubmit(handleRiskSubmit)} className="space-y-4">
            <h2 className="text-lg font-semibold">Perfil de Riesgo</h2>
            <p className="text-gray-500 text-sm">Evalua los factores de riesgo del cliente</p>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sector/Industria (0-30)
                </label>
                <input
                  type="number"
                  min="0"
                  max="30"
                  {...riskForm.register('sector_score', { valueAsNumber: true })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Jurisdiccion/ Pais (0-20)
                </label>
                <input
                  type="number"
                  min="0"
                  max="20"
                  {...riskForm.register('jurisdiction_score', { valueAsNumber: true })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Persona Expuesta Politicamente (0-20)
                </label>
                <input
                  type="number"
                  min="0"
                  max="20"
                  {...riskForm.register('pep_score', { valueAsNumber: true })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Volumen de Transacciones (0-20)
                </label>
                <input
                  type="number"
                  min="0"
                  max="20"
                  {...riskForm.register('volume_score', { valueAsNumber: true })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Origen de Fondos (0-10)
                </label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  {...riskForm.register('funds_origin_score', { valueAsNumber: true })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
            </div>

            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="flex-1 bg-gray-200 text-gray-700 py-2 rounded hover:bg-gray-300"
              >
                Volver
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {isSubmitting ? 'Calculando...' : 'Calcular Riesgo'}
              </button>
            </div>
          </form>
        )}

        {step === 3 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">Documentos</h2>
            <p className="text-gray-500">Funcionalidad de documentacion - en desarrollo</p>
            <p className="text-sm text-gray-400">El backend almacena metadata de documentos</p>

            <div className="flex gap-2">
              <button
                onClick={() => setStep(2)}
                className="flex-1 bg-gray-200 text-gray-700 py-2 rounded hover:bg-gray-300"
              >
                Volver
              </button>
              <button
                onClick={() => setStep(4)}
                className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
              >
                Continuar
              </button>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">Revision y Envio</h2>

            {riskResult && (
              <div className="bg-gray-50 p-4 rounded">
                <h3 className="font-medium mb-2">Resultado del Analisis de Riesgo</h3>
                {riskResult.calculation_aborted ? (
                  <div className="bg-red-100 border border-red-300 text-red-700 p-3 rounded">
                    <p className="font-medium">⚠️ CALCULO ABORTADO</p>
                    <p className="text-sm">Se detecto coincidencia con lista de sanciones. El expediente sera bloqueado.</p>
                  </div>
                ) : (
                  <div>
                    <p>Puntaje Total: {riskResult.total_score}</p>
                    <p>Nivel de Riesgo: {riskResult.risk_level}</p>
                  </div>
                )}
              </div>
            )}

            <div className="bg-gray-50 p-4 rounded">
              <h3 className="font-medium mb-2">Datos del Cliente</h3>
              <p>Nombre: {clientForm.getValues('client_name')}</p>
              <p>Tipo Documento: {clientForm.getValues('client_id_type')}</p>
              <p>Pais: {clientForm.getValues('client_country')}</p>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setStep(3)}
                className="flex-1 bg-gray-200 text-gray-700 py-2 rounded hover:bg-gray-300"
              >
                Volver
              </button>
              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="flex-1 bg-green-600 text-white py-2 rounded hover:bg-green-700 disabled:opacity-50"
              >
                {isSubmitting ? 'Enviando...' : 'Enviar a Revision'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}