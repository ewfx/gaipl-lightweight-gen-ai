import dayjs from 'dayjs';

export interface IIncident {
  id?: number;
  incidentnum?: string | null;
  shortDescription?: string | null;
  descrption?: string | null;
  status?: string | null;
  priority?: string | null;
  openedAt?: dayjs.Dayjs | null;
  resolvedAt?: dayjs.Dayjs | null;
}

export const defaultValue: Readonly<IIncident> = {};
