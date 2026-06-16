import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import StepWizard from '../components/StepWizard';
import {
  clientSchema,
  riskProfileSchema,
  SECTOR_OPTIONS,
  JURISDICTION_OPTIONS,
  PEP_OPTIONS,
  VOLUME_OPTIONS,
  FUNDS_ORIGIN_OPTIONS,
  DOCUMENT_TYPE_OPTIONS,
  getScoreFromValue,
  getLabelFromValue,
} from '../schemas/caseFile';

type ClientForm = z.infer<typeof clientSchema>;
type RiskForm = z.infer<typeof riskProfileSchema>;

const ID_TYPES = ['DNI', 'PASAPARTE', 'CEDULA'];
const COUNTRIES = ['Panama', 'Costa Rica', 'Argentina', 'Brasil', 'Colombia', 'Mexico', 'Uruguay', 'Peru', 'Chile'];

interface UploadedDocument {
  id: number;
  document_type: string;
  filename: string;
  file_path: string;
  size: number;
}

export default function CaseFileForm() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [caseFileId, setCaseFileId] = useState<number | null>(null);
  const [riskResult, setRiskResult] = useState<any>(null);
  const [documents, setDocuments] = useState<UploadedDocument[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitMessage, setSubmitMessage] = useState<{ type: 'success' | 'info'; text: string } | null>(null);

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
    resolver: zodResolver(riskProfileSchema),
    defaultValues: {
      sector_economico: '',
      jurisdiccion: '',
      pep_status: '',
      volumen_transacciones: '',
      origen_fondos: '',
    },
  });

  const steps = [
    { id: 1, name: 'Datos del Cliente' },
    { id: 2, name: 'Perfil de Riesgo' },
    { id: 3, name: 'Documentos y Envio' },
  ];

  // Preview de riesgo en tiempo real
  const previewRisk = () => {
    const values = riskForm.watch();
    if (!values.sector_economico || !values.jurisdiccion) return null;

    const s = getScoreFromValue(values.sector_economico, SECTOR_OPTIONS);
    const j = getScoreFromValue(values.jurisdiccion, JURISDICTION_OPTIONS);
    const p = getScoreFromValue(values.pep_status, PEP_OPTIONS);
    const v = getScoreFromValue(values.volumen_transacciones, VOLUME_OPTIONS);
    const o = getScoreFromValue(values.origen_fondos, FUNDS_ORIGIN_OPTIONS);

    return { s, j, p, v, o, total: s + j + p + v + o };
  };

  const preview = previewRisk();

  const handleClientSubmit = async (data: ClientForm) => {
    try {
      setIsSubmitting(true);
      setError(null);
      const response = await api.post('/case-files', data);
      setCaseFileId(response.data.id);
      setStep(2);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al crear el expediente');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRiskSubmit = async (data: RiskForm) => {
    if (!caseFileId) return;

    try {
      setIsSubmitting(true);
      setError(null);
      const response = await api.post(`/case-files/${caseFileId}/risk-assessment`, data);
      setRiskResult(response.data);
      setStep(3);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al evaluar riesgo');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDocumentUpload = async (documentType: string, file: File) => {
    if (!caseFileId) return;

    const formData = new FormData();
    formData.append('document_type', documentType);
    formData.append('file', file);

    try {
      const response = await api.post(`/case-files/${caseFileId}/documents`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setDocuments(prev => [...prev, response.data]);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al subir documento');
    }
  };

  const handleRemoveDocument = async (docId: number) => {
    try {
      await api.delete(`/case-files/${caseFileId}/documents/${docId}`);
      setDocuments(prev => prev.filter(d => d.id !== docId));
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al eliminar documento');
    }
  };

  const handleFinalSubmit = async () => {
    if (!caseFileId) return;

    const isClientValid = await clientForm.trigger();
    if (!isClientValid) {
      setStep(1);
      return;
    }

    const isRiskValid = await riskForm.trigger();
    if (!isRiskValid) {
      setStep(2);
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      setSubmitMessage(null);
      const response = await api.post(`/case-files/${caseFileId}/submit`);
      if (response.data.status === 'APROBADO') {
        setSubmitMessage({ type: 'success', text: '✓ Expediente aprobado automaticamente por riesgo BAJO' });
      } else if (response.data.status === 'EN_REVISION') {
        setSubmitMessage({ type: 'info', text: '✓ Expediente enviado a revision del Oficial de Cumplimiento' });
      } else {
        navigate('/case-files');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al enviar expediente');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Nuevo Expediente DDC</h1>

      <StepWizard steps={steps} currentStep={step} onStepClick={(s) => s < step && setStep(s)} />

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
          {error}
        </div>
      )}

      {submitMessage && (
        <div className={`mb-4 p-4 rounded text-sm ${
          submitMessage.type === 'success'
            ? 'bg-green-50 border border-green-200 text-green-700'
            : 'bg-blue-50 border border-blue-200 text-blue-700'
        }`}>
          {submitMessage.text}
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6 mt-6">
        {/* PASO 1: Datos del Cliente */}
        {step === 1 && (
          <form onSubmit={clientForm.handleSubmit(handleClientSubmit)} className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-800">Datos del Cliente</h2>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nombre / Razon Social</label>
              <input
                {...clientForm.register('client_name')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="Nombre completo o razon social"
              />
              {clientForm.formState.errors.client_name && (
                <p className="text-red-500 text-sm mt-1">{clientForm.formState.errors.client_name.message}</p>
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
                  {ID_TYPES.map(t => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
                {clientForm.formState.errors.client_id_type && (
                  <p className="text-red-500 text-sm mt-1">{clientForm.formState.errors.client_id_type.message}</p>
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
                  <p className="text-red-500 text-sm mt-1">{clientForm.formState.errors.client_id_number.message}</p>
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
                {COUNTRIES.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
              {clientForm.formState.errors.client_country && (
                <p className="text-red-500 text-sm mt-1">{clientForm.formState.errors.client_country.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-blue-600 text-white py-2.5 rounded-md font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {isSubmitting ? 'Guardando...' : 'Continuar'}
            </button>
          </form>
        )}

        {/* PASO 2: Perfil de Riesgo */}
        {step === 2 && (
          <form onSubmit={riskForm.handleSubmit(handleRiskSubmit)} className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-800">Perfil de Riesgo</h2>
            <p className="text-gray-500 text-sm">Selecciona los datos del cliente. El sistema calculara el riesgo automaticamente.</p>

            <div className="space-y-4">
              {/* Sector Economico */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Sector Economico</label>
                <select
                  {...riskForm.register('sector_economico')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="">Seleccionar sector...</option>
                  {SECTOR_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
                {riskForm.formState.errors.sector_economico && (
                  <p className="text-red-500 text-sm mt-1">{riskForm.formState.errors.sector_economico.message}</p>
                )}
              </div>

              {/* Jurisdiccion */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Jurisdiccion / Pais</label>
                <select
                  {...riskForm.register('jurisdiccion')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="">Seleccionar pais...</option>
                  {JURISDICTION_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
                {riskForm.formState.errors.jurisdiccion && (
                  <p className="text-red-500 text-sm mt-1">{riskForm.formState.errors.jurisdiccion.message}</p>
                )}
              </div>

              {/* PEP */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Condicion PEP</label>
                <select
                  {...riskForm.register('pep_status')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="">Seleccionar...</option>
                  {PEP_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
                {riskForm.formState.errors.pep_status && (
                  <p className="text-red-500 text-sm mt-1">{riskForm.formState.errors.pep_status.message}</p>
                )}
              </div>

              {/* Volumen */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Volumen Transacciones Esperado</label>
                <select
                  {...riskForm.register('volumen_transacciones')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="">Seleccionar...</option>
                  {VOLUME_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
                {riskForm.formState.errors.volumen_transacciones && (
                  <p className="text-red-500 text-sm mt-1">{riskForm.formState.errors.volumen_transacciones.message}</p>
                )}
              </div>

              {/* Origen Fondos */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Origen de Fondos</label>
                <select
                  {...riskForm.register('origen_fondos')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="">Seleccionar...</option>
                  {FUNDS_ORIGIN_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
                {riskForm.formState.errors.origen_fondos && (
                  <p className="text-red-500 text-sm mt-1">{riskForm.formState.errors.origen_fondos.message}</p>
                )}
              </div>
            </div>

            {/* Preview de Riesgo */}
            {preview && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <h3 className="font-medium text-gray-700 mb-2">Preview de Riesgo</h3>
                <div className="grid grid-cols-6 gap-2 text-center text-sm">
                  <div className="bg-white p-2 rounded">
                    <div className="text-gray-500">S</div>
                    <div className="font-bold">{preview.s}</div>
                  </div>
                  <div className="bg-white p-2 rounded">
                    <div className="text-gray-500">J</div>
                    <div className="font-bold">{preview.j}</div>
                  </div>
                  <div className="bg-white p-2 rounded">
                    <div className="text-gray-500">P</div>
                    <div className="font-bold">{preview.p}</div>
                  </div>
                  <div className="bg-white p-2 rounded">
                    <div className="text-gray-500">V</div>
                    <div className="font-bold">{preview.v}</div>
                  </div>
                  <div className="bg-white p-2 rounded">
                    <div className="text-gray-500">O</div>
                    <div className="font-bold">{preview.o}</div>
                  </div>
                  <div className="bg-blue-100 p-2 rounded">
                    <div className="text-gray-500">Total</div>
                    <div className="font-bold text-blue-700">{preview.total}</div>
                  </div>
                </div>
                <p className="text-sm text-gray-500 mt-2">
                  Nivel estimado: {' '}
                  {preview.total <= 30 && <span className="text-green-600 font-medium">BAJO (0-30)</span>}
                  {preview.total > 30 && preview.total <= 60 && <span className="text-yellow-600 font-medium">MEDIO (31-60)</span>}
                  {preview.total > 60 && preview.total <= 90 && <span className="text-orange-600 font-medium">ALTO (61-90)</span>}
                  {preview.total > 90 && <span className="text-red-600 font-medium">MUY ALTO (91+)</span>}
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  El calculo final incluye screening de sanciones y puede diferir.
                </p>
              </div>
            )}

            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="flex-1 bg-gray-200 text-gray-700 py-2.5 rounded-md font-medium hover:bg-gray-300"
              >
                Volver
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 bg-blue-600 text-white py-2.5 rounded-md font-medium hover:bg-blue-700 disabled:opacity-50"
              >
                {isSubmitting ? 'Evaluando...' : 'Continuar'}
              </button>
            </div>
          </form>
        )}

        {/* PASO 3: Documentos y Envio */}
        {step === 3 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-800">Documentos y Envio</h2>

            {/* Resultado del Analisis */}
            {riskResult && (
              <div className={`p-4 rounded-lg border ${
                riskResult.calculation_aborted
                  ? 'bg-red-50 border-red-300 text-red-800'
                  : 'bg-gray-50 border-gray-200'
              }`}>
                <h3 className="font-medium mb-2">Resultado del Analisis de Riesgo</h3>
                {riskResult.calculation_aborted ? (
                  <div>
                    <p className="font-bold text-red-700">⚠️ Se detecto coincidencia en listas de sanciones. El expediente sera revisado por el Oficial de Cumplimiento.</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-gray-500 text-sm">Puntaje Total: </span>
                      <span className="font-bold">{riskResult.total_score}</span>
                    </div>
                    <div>
                      <span className="text-gray-500 text-sm">Nivel: </span>
                      <span className={`font-bold ${
                        riskResult.risk_level === 'BAJO' ? 'text-green-600' :
                        riskResult.risk_level === 'MEDIO' ? 'text-yellow-600' :
                        riskResult.risk_level === 'ALTO' ? 'text-orange-600' : 'text-red-600'
                      }`}>
                        {riskResult.risk_level}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Resumen del Cliente */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-medium text-gray-700 mb-2">Datos del Cliente</h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <p><span className="text-gray-500">Nombre:</span> {clientForm.getValues('client_name')}</p>
                <p><span className="text-gray-500">Tipo ID:</span> {clientForm.getValues('client_id_type')}</p>
                <p><span className="text-gray-500">Numero:</span> {clientForm.getValues('client_id_number')}</p>
                <p><span className="text-gray-500">Pais:</span> {clientForm.getValues('client_country')}</p>
              </div>
            </div>

            {/* Perfil de Riesgo */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-medium text-gray-700 mb-2">Perfil de Riesgo</h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <p><span className="text-gray-500">Sector:</span> {getLabelFromValue(riskForm.getValues('sector_economico'), SECTOR_OPTIONS)}</p>
                <p><span className="text-gray-500">Jurisdiccion:</span> {getLabelFromValue(riskForm.getValues('jurisdiccion'), JURISDICTION_OPTIONS)}</p>
                <p><span className="text-gray-500">PEP:</span> {getLabelFromValue(riskForm.getValues('pep_status'), PEP_OPTIONS)}</p>
                <p><span className="text-gray-500">Volumen:</span> {getLabelFromValue(riskForm.getValues('volumen_transacciones'), VOLUME_OPTIONS)}</p>
                <p><span className="text-gray-500">Origen fondos:</span> {getLabelFromValue(riskForm.getValues('origen_fondos'), FUNDS_ORIGIN_OPTIONS)}</p>
              </div>
            </div>

            {/* Documentos */}
            <div className="border-t pt-4">
              <h3 className="font-medium text-gray-700 mb-3">Documentos Adjuntos</h3>
              {documents.length === 0 ? (
                <p className="text-gray-400 text-sm mb-3">No hay documentos adjuntos</p>
              ) : (
                <ul className="space-y-2 mb-3">
                  {documents.map((doc) => (
                    <li key={doc.id} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                      <div className="text-sm">
                        <span className="font-medium">{getLabelFromValue(doc.document_type, DOCUMENT_TYPE_OPTIONS)}</span>
                        <span className="text-gray-500 ml-2">{doc.filename}</span>
                        <span className="text-gray-400 ml-2">({(doc.size / 1024).toFixed(1)} KB)</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoveDocument(doc.id)}
                        className="text-red-500 text-sm hover:underline"
                      >
                        Quitar
                      </button>
                    </li>
                  ))}
                </ul>
              )}

              {/* Upload Form */}
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <p className="text-sm font-medium text-gray-700 mb-2">Agregar documento</p>
                <div className="flex gap-2 items-end">
                  <div className="flex-1">
                    <label className="block text-xs text-gray-500 mb-1">Tipo de documento</label>
                    <select
                      id="docTypeSelect"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    >
                      {DOCUMENT_TYPE_OPTIONS.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </select>
                  </div>
                  <div className="flex-1">
                    <label className="block text-xs text-gray-500 mb-1">Archivo</label>
                    <input
                      type="file"
                      id="docFileInput"
                      className="w-full text-sm text-gray-500 file:mr-3 file:py-1.5 file:px-4 file:rounded file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-600 hover:file:bg-blue-100"
                    />
                  </div>
                  <button
                    type="button"
                    onClick={async () => {
                      const select = document.getElementById('docTypeSelect') as HTMLSelectElement;
                      const input = document.getElementById('docFileInput') as HTMLInputElement;
                      if (!input.files?.length) return;
                      const file = input.files[0];
                      await handleDocumentUpload(select.value, file);
                      input.value = '';
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700"
                  >
                    Subir
                  </button>
                </div>
                <p className="text-xs text-gray-400 mt-2">
                  PDF, PNG, JPG, DOC, XLS hasta 10MB
                </p>
              </div>
            </div>

            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setStep(2)}
                className="flex-1 bg-gray-200 text-gray-700 py-2.5 rounded-md font-medium hover:bg-gray-300"
              >
                Volver
              </button>
              <button
                onClick={handleFinalSubmit}
                disabled={isSubmitting}
                className="flex-1 bg-green-600 text-white py-2.5 rounded-md font-medium hover:bg-green-700 disabled:opacity-50"
              >
                {isSubmitting ? 'Enviando...' : 'Finalizar Expediente'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
