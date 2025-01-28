import { computed } from 'vue';
import { email, helpers, required, requiredIf } from '@vuelidate/validators';
import { useOrderFormStore } from '@/stores/useOrderFormStore';
import { useOrderStore } from '@/stores/useOrderStore';
import { isIncorrectDate, isValidStatusFuture, isValidStatusPast } from './validation';

import type { IOrderStatus } from 'shared/types';

export const rules = () => {
  const { formModel: form } = useOrderFormStore();
  const orderStore = useOrderStore();
  const airGroupModel = computed(() => orderStore.airGroupModel);
  const isFuelQuantityRequired = computed(
    () =>
      !form?.fuel_order?.is_open_release &&
      (!airGroupModel.value || airGroupModel.value?.length === 1)
  );

  const fuelOrderRules = form?.type?.is_fuel
    ? {
        arrival_datetime_utc: {
          required,
          arrivalLocationValidation: helpers.withMessage(
            'Arrival Date inconsistency between Arrival and Departure Date',
            (value: Date) => {
              return isIncorrectDate(form.fuel_order!.departure_datetime_utc, value.toString());
            }
          )
        },
        departure_datetime_utc: {
          required,
          departureLocationValidation: helpers.withMessage(
            'Departure Date inconsistency between Arrival and Departure Date',
            (value: Date) => {
              return isIncorrectDate(value.toString(), form?.fuel_order!.arrival_datetime_utc);
            }
          )
        },
        fuel_category: { required },
        fuel_quantity: {
          requiredIf: requiredIf(() => {
            return isFuelQuantityRequired.value;
          }),
          positiveValidation: helpers.withMessage(
            'Value should be greater than 0',
            (value: string) => {
              return isFuelQuantityRequired.value ? parseFloat(value) > 0 : true;
            }
          )
        },
        fuel_uom: {
          requiredIf: requiredIf(() => {
            return isFuelQuantityRequired.value;
          })
        },
        post_pre_minutes: {
          requiredIf: requiredIf(() => {
            return !form?.fuel_order?.is_open_release;
          }),
          positiveValidation: helpers.withMessage(
            'Value should be greater than 0',
            (value: string) => {
              return form?.fuel_order?.is_open_release || parseInt(value) > 0;
            }
          )
        }
      }
    : {};

  const ghOrderRules = form?.type?.is_gh
    ? {
        mission_type: { required },
        arrival_datetime_utc: {
          required,
          arrivalLocationValidation: helpers.withMessage(
            'Arrival Date inconsistency between Arrival and Departure Date',
            (value: Date) => {
              return isIncorrectDate(form?.gh_order!.departure_datetime_utc, value.toString());
            }
          )
        },
        departure_datetime_utc: {
          required,
          departureLocationValidation: helpers.withMessage(
            'Departure Date inconsistency between Arrival and Departure Date',
            (value: Date) => {
              return isIncorrectDate(value.toString(), form?.gh_order!.arrival_datetime_utc);
            }
          )
        }
      }
    : {};

  return {
    form: {
      status: {
        required,
        statusValidationPast: helpers.withMessage(
          'You are attempting to create a retrospective order type. Please correct the order dates or status and try again.',
          (value: IOrderStatus) => {
            const date = form?.type?.is_fuel
              ? form?.fuel_order?.fueling_on === 'A'
                ? new Date(
                    new Date(form.fuel_order!.arrival_datetime_utc!).getTime() +
                      form.fuel_order!.post_pre_minutes! * 60 * 1000
                  ).getTime()
                : new Date(
                    new Date(form.fuel_order!.departure_datetime_utc!).getTime() -
                      form.fuel_order!.post_pre_minutes! * 60 * 1000
                  ).getTime()
              : form?.gh_order!.arrival_datetime_utc;
            return isValidStatusPast(date, value.id);
          }
        ),
        statusValidationFuture: helpers.withMessage(
          'You are attempting to create a new future order type that has a status of Done. Please correct the order dates or status and try again.',
          (value: IOrderStatus) => {
            const date = form?.type?.is_fuel
              ? form.fuel_order?.arrival_datetime_utc
              : form?.gh_order!.arrival_datetime_utc;
            return isValidStatusFuture(date, value.id);
          }
        )
      },
      company: { required },
      type: { required },
      callsign: { required },
      client: { required },
      location: { required },
      flight_type: { required },
      aircraft: {
        requiredIf: requiredIf(() => {
          const aircraftType = form.aircraft_type;
          return !aircraftType && !form.is_any_aircraft;
        })
      },
      aircraft_type: {
        requiredIf: requiredIf(() => {
          const aircraft = form.aircraft;
          return !aircraft && !form.is_any_aircraft;
        })
      },
      destination: {
        requiredIf: requiredIf(() => {
          const destinationIntDom = form.destination_int_dom;
          return !destinationIntDom && !form?.fuel_order?.is_open_release;
        })
      },
      destination_int_dom: {
        requiredIf: requiredIf(() => {
          const destination = form.destination;
          return !destination && !form?.fuel_order?.is_open_release;
        })
      },
      fuel_order: fuelOrderRules,
      gh_order: ghOrderRules
    }
  };
};

export const personRules = () => {
  return {
    form: {
      details: {
        first_name: { required },
        last_name: { required },
        contact_email: { required, email },
        title: { required }
      },
      jobs: {
        role: { required },
        job_title: { required }
      }
    }
  };
};
