import { z } from 'zod';

export const clientSchema = z.object({
  name: z.string().min(2, 'Nombre requerido'),
  id_type: z.string().min(1, 'Tipo de ID requerido'),
  id_number: z.string().min(1, 'Numero de ID requerido'),
  country: z.string().min(1, 'Pais requerido'),
});

export type ClientForm = z.infer<typeof clientSchema>;