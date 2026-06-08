import { z } from 'zod';

export const caseFileCreateSchema = z.object({
  client_name: z.string().min(2, 'Nombre requerido'),
  client_id_type: z.string().min(1, 'Tipo de ID requerido'),
  client_id_number: z.string().min(1, 'Numero de ID requerido'),
  client_country: z.string().min(1, 'Pais requerido'),
});

export const caseFileUpdateSchema = z.object({
  current_step: z.number().optional(),
  status: z.string().optional(),
});

export const riskProfileSchema = z.object({
  sector_score: z.number().min(0).max(30),
  jurisdiction_score: z.number().min(0).max(20),
  pep_score: z.number().min(0).max(20),
  volume_score: z.number().min(0).max(20),
  funds_origin_score: z.number().min(0).max(10),
});

export const submitSchema = z.object({
  justification: z.string().optional(),
});

export type CaseFileCreateForm = z.infer<typeof caseFileCreateSchema>;
export type RiskProfileForm = z.infer<typeof riskProfileSchema>;