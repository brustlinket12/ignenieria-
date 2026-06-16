export type User = {
  id: number;
  email: string;
  name: string;
  role: 'ANALISTA' | 'OFICIAL_CUMPLIMIENTO' | 'OFICIAL_AUDITORIA';
  created_at: string;
};

export type Client = {
  id: number;
  name: string;
  id_type: string;
  id_number: string;
  country: string;
  created_at: string;
};

export type RiskAssessment = {
  id: number;
  case_file_id: number;
  sector_score: number;
  jurisdiction_score: number;
  pep_score: number;
  volume_score: number;
  funds_origin_score: number;
  sanctions_score: number;
  total_score: number | null;
  risk_level: 'BAJO' | 'MEDIO' | 'ALTO' | 'MUY_ALTO' | null;
  calculation_aborted: boolean;
  created_at: string;
};

export type SanctionsScreening = {
  id: number;
  case_file_id: number;
  provider: string;
  result: 'SIN_COINCIDENCIA' | 'COINCIDENCIA_PARCIAL' | 'COINCIDENCIA_CONFIRMADA' | 'ERROR_CONSULTA';
  matched_name: string | null;
  matched_list: string | null;
  raw_response: string | null;
  created_at: string;
};

export type Alert = {
  id: number;
  case_file_id: number;
  type: string;
  message: string;
  read: boolean;
  created_at: string;
};

export type AuditLog = {
  id: number;
  case_file_id: number | null;
  user_id: number;
  event_type: string;
  payload: string | null;
  created_at: string;
  user?: User;
};

export type CaseFile = {
  id: number;
  client_id: number;
  client: Client;
  status: 'BORRADOR' | 'EN_REVISION' | 'APROBADO' | 'RECHAZADO' | 'REQUIERE_CORRECCION';
  current_step: number;
  blocked_by_sanctions: boolean;
  created_by: number;
  reviewed_by: number | null;
  created_at: string;
  updated_at: string;
  submitted_at: string | null;
  approved_at: string | null;
  rejected_at: string | null;
  risk_assessment: RiskAssessment | null;
  sanctions_screening: SanctionsScreening[];
};

export type CaseFileCreate = {
  client_name: string;
  client_id_type: string;
  client_id_number: string;
  client_country: string;
};

export type RiskProfileData = {
  sector_score: number;
  jurisdiction_score: number;
  pep_score: number;
  volume_score: number;
  funds_origin_score: number;
};
