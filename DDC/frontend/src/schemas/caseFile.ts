import { z } from 'zod';

// =============================================================================
// CATALOGOS DE OPCIONES - Segun PRD Ley 23/2015 Panama
// =============================================================================

export const SECTOR_OPTIONS = [
  { value: "BANCO_FINANCIERA_REGULADA", label: "Banco / Empresa financiera regulada", score: 5 },
  { value: "FIDUCIARIA_CASA_VALORES", label: "Fiduciaria / Casa de valores", score: 10 },
  { value: "COMERCIO_GENERAL", label: "Comercio general", score: 10 },
  { value: "CONSTRUCCION", label: "Construccion", score: 15 },
  { value: "BIENES_RAICES_VEHICULOS_EMPENO_METALES", label: "Bienes raices / Vehiculos / Empeno / Metales / Piedras", score: 20 },
  { value: "CASINOS_JUEGOS_AZAR", label: "Casinos y juegos de azar", score: 25 },
  { value: "OTRO_SECTOR", label: "Otro sector no listado", score: 10 },
];

export const JURISDICTION_OPTIONS = [
  // Nivel Bajo
  { value: "PANAMA", label: "Panama", score: 5 },
  { value: "COSTA_RICA", label: "Costa Rica", score: 5 },
  { value: "EEUU", label: "Estados Unidos", score: 5 },
  { value: "CANADA", label: "Canada", score: 5 },
  { value: "ESPANA", label: "Espana", score: 5 },
  // Nivel Medio
  { value: "COLOMBIA", label: "Colombia", score: 10 },
  { value: "MEXICO", label: "Mexico", score: 10 },
  { value: "BRASIL", label: "Brasil", score: 10 },
  { value: "ARGENTINA", label: "Argentina", score: 10 },
  { value: "PERU", label: "Peru", score: 10 },
  // Nivel Alto
  { value: "VENEZUELA", label: "Venezuela", score: 15 },
  { value: "HAITI", label: "Haiti", score: 15 },
  // Nivel Muy Alto
  { value: "IRAN", label: "Iran", score: 20 },
  { value: "COREA_DEL_NORTE", label: "Corea del Norte", score: 20 },
  // Otro
  { value: "OTRO_PAIS", label: "Otro pais", score: 5 },
];

export const PEP_OPTIONS = [
  { value: "NO_PEP", label: "No es PEP", score: 0 },
  { value: "PEP_NACIONAL", label: "PEP Nacional", score: 10 },
  { value: "PEP_EXTRANJERO", label: "PEP Extranjero", score: 20 },
  { value: "RELACIONADO_PEP", label: "Relacionado a PEP", score: 15 },
];

export const VOLUME_OPTIONS = [
  { value: "BAJO", label: "Bajo", score: 5 },
  { value: "MEDIO", label: "Medio", score: 10 },
  { value: "ALTO", label: "Alto", score: 20 },
];

export const FUNDS_ORIGIN_OPTIONS = [
  { value: "SALARIO_RELACION_LABORAL", label: "Salario / Relacion laboral", score: 0 },
  { value: "ACTIVIDAD_COMERCIAL_DECLARADA", label: "Actividad comercial declarada", score: 5 },
  { value: "INVERSIONES_PATRIMONIO", label: "Inversiones / Patrimonio", score: 5 },
  { value: "TERCEROS", label: "Fondos de terceros", score: 10 },
  { value: "NO_JUSTIFICADO", label: "No justificado", score: 10 },
];

export const DOCUMENT_TYPE_OPTIONS = [
  { value: "IDENTIFICACION", label: "Identificacion del cliente" },
  { value: "COMPROBANTE_DOMICILIO", label: "Comprobante de domicilio" },
  { value: "ORIGEN_FONDOS", label: "Declaracion de origen de fondos" },
  { value: "DOCUMENTO_SOCIETARIO", label: "Documento societario / Registro mercantil" },
  { value: "SOPORTE_ACTIVIDAD", label: "Soporte de actividad economica" },
  { value: "OTRO", label: "Otro documento" },
];

// =============================================================================
// ESQUEMAS ZOD
// =============================================================================

export const clientSchema = z.object({
  client_name: z.string().min(2, 'Nombre requerido'),
  client_id_type: z.string().min(1, 'Tipo de ID requerido'),
  client_id_number: z.string().min(1, 'Numero de ID requerido'),
  client_country: z.string().min(1, 'Pais requerido'),
});

export const riskProfileSchema = z.object({
  sector_economico: z.string().min(1, 'Sector economico requerido'),
  jurisdiccion: z.string().min(1, 'Jurisdiccion requerida'),
  pep_status: z.string().min(1, 'Condicion PEP requerida'),
  volumen_transacciones: z.string().min(1, 'Volumen requerido'),
  origen_fondos: z.string().min(1, 'Origen de fondos requerido'),
});

export const submitSchema = z.object({
  justification: z.string().optional(),
});

// =============================================================================
// HELPERS
// =============================================================================

export function getScoreFromValue(value: string, options: typeof SECTOR_OPTIONS): number {
  const option = options.find(o => o.value === value);
  return option?.score || 0;
}

export function getLabelFromValue(value: string, options: typeof SECTOR_OPTIONS): string {
  const option = options.find(o => o.value === value);
  return option?.label || value;
}

export type CaseFileCreateForm = z.infer<typeof clientSchema>;
export type RiskProfileForm = z.infer<typeof riskProfileSchema>;
