<template>
  <div v-if="props.isOpen" class="order-modal old-system-modal">
    <div class="order-modal-wrapper">
      <div ref="target" class="order-modal-container">
        <div class="order-modal-body">
          <OrderForm add-default-classes is-modal>
            <template #header>
              <div class="header w-full flex justify-between">
                <div class="text-[1.25rem] font-medium text-grey-1000">
                  Order Details for Old System
                </div>
                <button @click.stop="emit('modal-close')">
                  <img
                    width="12"
                    height="12"
                    src="../../assets/icons/cross.svg"
                    alt="delete"
                    class="close"
                  />
                </button>
              </div>
            </template>
            <template #content>
              <div class="form-body-wrapper">
                <div class="old-system-modal-header pb-[0.75rem]">“Price” Table Row Selection</div>
                <div class="old-system-modal-item gap-3 flex pb-[0.75rem]">
                  <div class="w-5/12 old-system-modal-name flex items-start">Supplier</div>
                  <div class="w-7/12 old-system-modal-value">
                    <span class="cursor-pointer relative" @click="copy($event as PointerEvent)"
                      >{{ order?.fuel_order?.supplier?.full_repr }}
                    </span>
                  </div>
                </div>
                <div class="old-system-modal-item gap-3 flex pb-[0.75rem]">
                  <div class="w-5/12 old-system-modal-name flex items-start">Client</div>
                  <div class="w-7/12 old-system-modal-value">
                    <span class="cursor-pointer relative" @click="copy($event as PointerEvent)">{{
                      order?.client?.full_repr
                    }}</span>
                  </div>
                </div>
                <div class="old-system-modal-item gap-3 flex pb-[0.75rem]">
                  <div class="w-5/12 old-system-modal-name flex items-start">IPA</div>
                  <div class="w-7/12 old-system-modal-value">
                    <span class="cursor-pointer relative" @click="copy($event as PointerEvent)">{{
                      order?.fuel_order?.ipa?.full_repr ?? '--'
                    }}</span>
                  </div>
                </div>
                <div class="relative"><div class="old-system-modal-divider"></div></div>
                <div class="old-system-modal-header py-[0.75rem]">“Details” Form Fields</div>
                <div class="old-system-modal-item gap-3 flex pb-[0.75rem]">
                  <div class="w-5/12 old-system-modal-name flex items-start">Fuel or GH</div>
                  <div class="w-7/12 old-system-modal-value">
                    <span class="cursor-pointer relative" @click="copy($event as PointerEvent)"
                      >Fuel Order</span
                    >
                  </div>
                </div>
                <div class="old-system-modal-item gap-3 flex pb-[0.75rem]">
                  <div class="w-5/12 old-system-modal-name flex items-start">Order Type</div>
                  <div class="w-7/12 old-system-modal-value">
                    <span class="cursor-pointer relative" @click="copy($event as PointerEvent)">{{
                      order?.fuel_order?.is_open_release ? 'Open Release' : 'Normal'
                    }}</span>
                  </div>
                </div>
                <div class="old-system-modal-item gap-3 flex pb-[0.75rem]">
                  <div class="w-5/12 old-system-modal-name flex items-start">Aircraft / Type</div>
                  <div
                    v-if="order?.is_any_aircraft || order?.aircraft_type"
                    class="w-7/12 old-system-modal-value"
                  >
                    <span class="cursor-pointer relative" @click="copy($event as PointerEvent)">
                      {{
                        order?.is_any_aircraft ? 'Any Aircraft' : order?.aircraft_type?.full_repr
                      }}
                    </span>
                  </div>
                  <div v-else class="w-7/12 flex flex-col gap-1">
                    <div
                      v-for="aircraft in order?.tails"
                      :key="aircraft.id"
                      class="old-system-modal-value"
                    >
                      <span class="cursor-pointer relative" @click="copy($event as PointerEvent)">
                        {{ aircraft?.tail_number?.reg_icao_repr }}
                      </span>
                    </div>
                  </div>
                </div>
                <div class="old-system-modal-item gap-3 flex pb-[0.75rem]">
                  <div class="w-5/12 old-system-modal-name flex items-start">Operator</div>
                  <div class="w-7/12 old-system-modal-value">
                    <span class="cursor-pointer relative" @click="copy($event as PointerEvent)"
                      >{{ order?.operator?.details?.registered_name ?? '--' }}
                    </span>
                  </div>
                </div>
                <div class="old-system-modal-item gap-3 flex pb-[0.75rem]">
                  <div class="w-5/12 old-system-modal-name flex items-start">Flight Number</div>
                  <div class="w-7/12 old-system-modal-value">
                    <span class="cursor-pointer relative" @click="copy($event as PointerEvent)"
                      >{{ order?.callsign }}
                    </span>
                  </div>
                </div>
                <div class="old-system-modal-item gap-3 flex pb-[0.75rem]">
                  <div class="w-5/12 old-system-modal-name flex items-start">Type of Flight</div>
                  <div class="w-7/12 old-system-modal-value">
                    <span class="cursor-pointer relative" @click="copy($event as PointerEvent)"
                      >{{
                        order?.flight_type?.code === 'D' || order?.flight_type?.code === 'M'
                          ? 'Government / Military / Diplomatic'
                          : order?.is_private
                          ? 'Private'
                          : 'Non-Private (Commercial)'
                      }}
                    </span>
                  </div>
                </div>
                <div class="old-system-modal-item gap-3 flex pb-[0.75rem]">
                  <div class="w-5/12 old-system-modal-name flex items-start">Destination</div>
                  <div class="w-7/12 old-system-modal-value">
                    <span class="cursor-pointer relative" @click="copy($event as PointerEvent)">{{
                      order?.destination_int_dom?.name ?? '--'
                    }}</span>
                  </div>
                </div>
                <!-- TO DO: Add value when BE ready -->
                <div class="old-system-modal-item gap-3 flex pb-[0.75rem]">
                  <div class="w-5/12 old-system-modal-name flex items-start">
                    FBO / Handling Agent
                  </div>
                  <div class="w-7/12 old-system-modal-value">
                    <span class="cursor-pointer relative" @click="copy($event as PointerEvent)">
                      {{ order?.fuel_order?.ground_handler?.full_repr ?? '--' }}
                    </span>
                  </div>
                </div>
                <div class="old-system-modal-item gap-3 flex pb-[0.75rem]">
                  <div class="w-5/12 old-system-modal-name flex items-start">Arrival Date</div>
                  <div class="w-7/12 old-system-modal-value">
                    <span class="cursor-pointer relative" @click="copy($event as PointerEvent)">
                      {{
                        order?.fuel_order?.arrival_datetime_utc
                          ? toOldDateFormat(order?.fuel_order?.arrival_datetime_utc?.slice(0, 10))
                          : '--'
                      }}
                    </span>
                  </div>
                </div>
                <div class="old-system-modal-item gap-3 flex pb-[0.75rem]">
                  <div class="w-5/12 old-system-modal-name flex items-start">Arrival Time</div>
                  <div class="w-7/12 old-system-modal-value">
                    <span class="cursor-pointer relative" @click="copy($event as PointerEvent)">
                      {{
                        order?.fuel_order?.arrival_time_tbc
                          ? 'TBC'
                          : order?.fuel_order?.arrival_datetime_utc?.slice(11, 17)
                      }}
                    </span>
                  </div>
                </div>
                <div class="old-system-modal-item gap-3 flex pb-[0.75rem]">
                  <div class="w-5/12 old-system-modal-name flex items-start">Departure Date</div>
                  <div class="w-7/12 old-system-modal-value">
                    <span class="cursor-pointer relative" @click="copy($event as PointerEvent)">
                      {{
                        order?.fuel_order?.departure_datetime_utc
                          ? toOldDateFormat(order?.fuel_order?.departure_datetime_utc?.slice(0, 10))
                          : '--'
                      }}
                    </span>
                  </div>
                </div>
                <div class="old-system-modal-item gap-3 flex pb-[0.75rem]">
                  <div class="w-5/12 old-system-modal-name flex items-start">Departure Time</div>
                  <div class="w-7/12 old-system-modal-value">
                    <span class="cursor-pointer relative" @click="copy($event as PointerEvent)">
                      {{
                        order?.fuel_order?.departure_time_tbc
                          ? 'TBC'
                          : order?.fuel_order?.departure_datetime_utc?.slice(11, 17)
                      }}
                    </span>
                  </div>
                </div>
                <div class="old-system-modal-item gap-3 flex pb-[0.75rem]">
                  <div class="w-5/12 old-system-modal-name flex items-start">Delivery Required</div>
                  <div class="w-7/12 old-system-modal-value">
                    <span class="cursor-pointer relative" @click="copy($event as PointerEvent)"
                      >When Requested</span
                    >
                  </div>
                </div>
                <div class="old-system-modal-item gap-3 flex pb-[0.75rem]">
                  <div class="w-5/12 old-system-modal-name flex items-start">Destination ICAO</div>
                  <div class="w-7/12 old-system-modal-value">
                    <span class="cursor-pointer relative" @click="copy($event as PointerEvent)">
                      {{ order?.destination?.airport_details?.icao_code ?? '--' }}
                    </span>
                  </div>
                </div>
                <!-- TO DO: Replace with USG value when BE ready -->
                <div class="old-system-modal-item gap-3 flex pb-[0.75rem]">
                  <div class="w-5/12 old-system-modal-name flex items-start">
                    Estimated Uplift Volume (USG)
                  </div>
                  <div class="w-7/12 old-system-modal-value">
                    <span class="cursor-pointer relative" @click="copy($event as PointerEvent)">
                      {{ orderPricing?.scenario?.fuel_quantity_usg?.split('.')[0] ?? '--' }}
                    </span>
                  </div>
                </div>
              </div>
            </template>
          </OrderForm>
        </div>
        <div class="order-modal-footer">
          <button class="modal-button submit" @click.stop="emit('modal-close')">Done</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed, ref } from 'vue';
import { useOrderStore } from '@/stores/useOrderStore';
import OrderForm from '@/components/forms/OrderForm.vue';
import { useQuerySupplyFuel } from '@/services/queries';
import { toOldDateFormat } from '@/helpers/order';

const props = defineProps({
  isOpen: Boolean
});

const orderStore = useOrderStore();
const order = computed(() => orderStore.order);
const pricingRecord = computed(() => order.value?.pricing_calculation_record);

const emit = defineEmits(['modal-close', 'modal-submit']);

const target = ref(null);

const { data: orderPricing } = useQuerySupplyFuel(pricingRecord, {
  enabled: props.isOpen,
  retry: false
});

const copy = async (e: PointerEvent) => {
  const text = (e?.target as HTMLElement).innerText;
  if (text) {
    (e?.target as HTMLElement).classList.add('copied');
    await navigator.clipboard.writeText(text);
    setTimeout(() => {
      (e?.target as HTMLElement).classList.remove('copied');
    }, 2000);
  }
};
</script>

<style scoped lang="scss">
.old-system-modal {
  &-header {
    font-weight: 600;
    font-size: 15px;
    color: rgba(21, 28, 53, 1);
  }

  &-name {
    font-weight: 500;
    font-size: 13px;
    color: rgba(82, 90, 122, 1);
  }
  &-value {
    font-weight: 500;
    font-size: 14px;
    color: rgba(21, 28, 53, 1);
    &:hover {
      color: rgba(82, 90, 122, 1);
      span::after {
        content: '';
        display: inline-block;
        width: 12px;
        height: 12px;
        background-image: url('../../assets/icons/copy-06.svg');
        background-size: contain;
        background-repeat: no-repeat;
        margin-left: 4px;
      }
      span::before {
        content: 'Click to Copy';
        position: absolute;
        top: -40px;
        left: 0;
        background-color: rgba(21, 28, 53, 0.8);
        color: white;
        font-size: 14px;
        padding: 6px 12px;
        border-radius: 8px;
        white-space: nowrap;
        z-index: 10;
        opacity: 1;
        transform: translateY(0);
        transition: opacity 0.2s ease, transform 0.2s ease;
      }
      span.copied::before {
        content: 'Copied!';
      }
    }
    span::before {
      content: '';
      opacity: 0;
      transform: translateY(-5px);
      transition: opacity 0.2s ease, transform 0.2s ease;
    }
  }
  &-divider {
    position: absolute;
    width: calc(100% + 3rem);
    height: 1px;
    background: rgba(223, 226, 236, 1);
    top: 0rem;
    left: -1.5rem;
  }
}

.order-modal-footer {
  align-items: center;
  flex: 0 0 72px;
  min-height: 72px;

  .modal-button {
    max-height: 44px;
  }
}
</style>
