<template>
  <div v-if="isOpen" class="order-modal edit-quote-modal">
    <div class="order-modal-wrapper">
      <div ref="target" class="order-modal-container">
        <div class="order-modal-header w-full flex justify-between">
          <div class="text-[1.25rem] font-medium text-grey-1000">
            Enter Ground Handling Quote Details
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
        <div class="order-modal-body">
          <div class="form-body-wrapper px-[1.5rem] py-[1rem] pb-0">
            <div class="w-full flex gap-3">
              <div class="w-6/12">
                <SelectField
                  v-model="selectedOption"
                  label-text="Supplier"
                  placeholder=" "
                  label="display"
                  :disabled="true"
                  :options="[]"
                />
              </div>
              <div class="w-6/12">
                <InputField
                  v-model="selectedOption"
                  label-text="Supplier Reference"
                  placeholder="Enter Reference"
                />
              </div>
            </div>
            <div class="w-full flex gap-3">
              <SelectField
                v-model="selectedUom"
                class="w-6/12"
                label-text="Quotation Currency"
                placeholder=""
                label="description_plural"
                :options="[]"
              ></SelectField>
              <div class="flex flex-col w-6/12">
                <Label :required="false" label-text="Valid From (UTC)" class="whitespace-nowrap" />
                <FlatPickr
                  ref="departureDateRef"
                  v-model="toDateTime.date"
                  :config="flatpickerConfig"
                />
              </div>
            </div>
            <div class="flex items-center justify-start pb-[1rem] gap-3">
              <Button class="modal-button icon">
                <img
                  height="20"
                  width="20"
                  :src="getImageUrl('assets/icons/paperclip.svg')"
                  alt="attachment"
                />
              </Button>
              <p class="text-base whitespace-nowrap font-semibold text-main">Upload Quote File</p>
            </div>
            <div class="flex items-center justify-start pb-[1rem] ml-[0.7rem]">
              <CheckboxField v-model="typeSpecific" class="mb-0 mr-[0.75rem]" size="20px" />
              <p class="text-base whitespace-nowrap font-semibold text-main">Type-Specific?</p>
            </div>
          </div>
          <div v-if="aircrafts.length" class="edit-quote-modal-tabs flex px-[1.5rem] gap-3">
            <div
              v-for="(aircraft, index) in aircrafts"
              :key="aircraft.id"
              class="edit-quote-modal-tab py-[0.75rem]"
              :class="{ 'edit-quote-modal-tab-active': index === activeAircraftIndex }"
              @click="changeTab(index)"
            >
              {{ aircraft.tail_number?.full_repr }}
            </div>
          </div>
          <div class="edit-quote-modal-wrap p-[0.75rem]">
            <div class="handling-step-content">
              <div class="handling-step-content-header-sub flex">
                <div
                  class="handling-step-content-header-sub-wrap flex w-6/12 py-[0.5rem] pl-[0.75rem] gap-2"
                >
                  <div class="handling-step-content-header-sub-el flex w-6/12 justify-start">
                    Item
                  </div>
                  <div
                    class="handling-step-content-header-sub-el flex w-6/12 justify-start el-border pl-4"
                  >
                    Included in GH Fee
                  </div>
                </div>
                <div
                  class="handling-step-content-header-sub-wrap flex w-6/12 py-[0.5rem] pl-[0.75rem]"
                >
                  <div class="handling-step-content-header-sub-el flex w-full justify-center">
                    Application Method
                  </div>
                  <div class="handling-step-content-header-sub-el flex w-full justify-center">
                    Unit price
                  </div>
                  <div class="handling-step-content-header-sub-el flex w-3/12 justify-start">
                    &nbsp;
                  </div>
                </div>
              </div>
              <div
                v-for="service in orderServices"
                :key="service.id"
                class="handling-step-content-element flex"
              >
                <div
                  class="handling-step-content-element-wrap flex w-6/12 py-[0.5rem] pl-[0.75rem] el-border-light gap-2"
                >
                  <div
                    class="handling-step-content-element-el-name flex justify-start items-center w-6/12"
                  >
                    {{ service.handling_service.full_repr }}
                  </div>
                  <div
                    class="handling-step-content-element-el flex justify-center items-center w-6/12"
                  >
                    <CheckboxField
                      :model-value="service.applies_on_departure"
                      class="mb-0 mr-1"
                      size="20px"
                      :disabled="!service.is_editable || !service.handling_service.is_dep_available"
                    ></CheckboxField>
                  </div>
                </div>
                <div
                  class="handling-step-content-element-wrap flex w-6/12 py-[0.5rem] pl-[0.75rem] el-border-light gap-2"
                >
                  <div
                    class="handling-step-content-element-el flex justify-start items-center w-full pr-[0.75rem]"
                  >
                    <span class="text-light-subtitle pr-[0.5rem] text-[0.75rem]">x</span>
                    <div v-if="!service.is_editable" class="flex gap-2">
                      {{ service.quantity_text ?? '--' }}
                      {{ service.quantity_value ?? '' }}
                      {{ service.quantity_uom ?? '' }}
                    </div>
                    <InputField
                      v-else-if="service.handling_service.is_allowed_free_text"
                      :model-value="(service.quantity_text) as string"
                      class="w-full mb-0"
                      is-white
                      placeholder=" "
                    />
                    <div
                      v-else-if="service.handling_service.is_allowed_quantity_selection"
                      class="input-wrap flex w-full items-center"
                    >
                      <InputField
                        :model-value="(service.quantity_value) as string"
                        class="w-6/12 mb-0"
                        is-white
                        is-half
                        placeholder=" "
                      />
                      <SelectField
                        class="w-6/12 mb-0"
                        :is-white="true"
                        :is-half="true"
                        placeholder=" "
                        disabled
                        label="description_plural"
                        :model-value="service.quantity_uom!"
                      />
                    </div>
                    <div v-else class="flex gap-2">--</div>
                  </div>
                  <div
                    class="handling-step-content-element-el flex justify-between items-center w-3/12 px-[0.5rem] relative"
                  >
                    <img
                      v-if="service.is_deletable"
                      width="20"
                      height="20"
                      src="../../assets/icons/cross-red.svg"
                      alt="delete"
                      class="cursor-pointer"
                    />
                  </div>
                </div>
              </div>
              <div
                v-for="newService in newServices"
                :key="newService.id"
                class="handling-step-content-element new-service-element flex"
              >
                <div
                  class="handling-step-content-element-wrap flex w-6/12 py-[0.5rem] pl-[0.75rem] el-border-light gap-2"
                >
                  <div
                    class="handling-step-content-element-el-name flex justify-center items-center w-6/12"
                  >
                    <SelectField
                      class="w-full mb-0"
                      :is-white="true"
                      placeholder="Choose Service"
                      :options="displayServices"
                      label="name"
                      :model-value="newService.name"
                    />
                  </div>
                  <div
                    class="handling-step-content-element-el-name flex justify-center items-center w-6/12"
                  >
                    <CheckboxField
                      v-model="newService.applies_on_arrival"
                      class="mb-0 mr-1"
                      size="20px"
                      :background-color="'#fbfcfe'"
                      :disabled="!newService.is_arr_available || !newService.name"
                    ></CheckboxField>
                  </div>
                </div>
                <div
                  class="handling-step-content-element-wrap flex w-6/12 py-[0.5rem] pl-[0.75rem] el-border-light gap-2"
                >
                  <div
                    class="handling-step-content-element-el flex justify-start items-center w-6/12"
                  >
                    <div class="input-wrap flex items-center pr-[0.75rem] grow">
                      <span class="text-light-subtitle pr-[0.5rem] text-[0.75rem]">x</span>
                      <InputField
                        v-if="newService.is_allowed_free_text"
                        :model-value="newService.quantity"
                        class="w-full mb-0"
                        is-white
                        placeholder=" "
                        @update:model-value="
                          (value) => {
                            newService.quantity = value;
                          }
                        "
                      />
                      <div
                        v-else-if="newService.is_allowed_quantity_selection"
                        class="input-wrap flex w-full items-center"
                      >
                        <InputField
                          :model-value="newService.quantity_value"
                          class="w-6/12 mb-0"
                          is-white
                          is-half
                          placeholder=" "
                          @update:model-value="
                            (value) => {
                              newService.quantity_value = value;
                            }
                          "
                        />
                        <SelectField
                          class="w-6/12 mb-0"
                          :is-white="true"
                          :is-half="true"
                          placeholder=" "
                          disabled
                          label="description_plural"
                          :model-value="newService.quantity_selection_uom?.description_plural"
                        />
                      </div>
                      <div v-else>--</div>
                    </div>
                  </div>
                  <div
                    class="handling-step-content-element-el flex justify-between items-center w-full px-[0.5rem] gap-1 relative"
                  >
                    <Button class="button flex items-center button-cancel-service">
                      <img
                        width="20"
                        height="20"
                        src="../../assets/icons/cross-red.svg"
                        alt="delete"
                        class="cursor-pointer"
                      />
                    </Button>
                    <Button class="button flex items-center">Save</Button>
                  </div>
                </div>
              </div>
              <div
                class="handling-step-add-service flex cursor-pointer p-[0.75rem] gap-2 w-fit"
                @click="addNewService"
              >
                <img src="../../assets/icons/plus.svg" alt="add" />
                Add Service to Order
              </div>
            </div>
          </div>
        </div>
        <div class="order-modal-footer">
          <button class="modal-button cancel" @click.stop="emit('modal-close')">Cancel</button>
          <button class="modal-button submit" @click.stop="onValidate()">Submit</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { type PropType, type Ref, ref, toRaw, watch } from 'vue';
import { computed } from 'vue';
import { Button } from 'shared/components';
import { useOrderStore } from '@/stores/useOrderStore';
import { useQueryOrderServices } from '@/services/queries';
import { getImageUrl, getRandomId } from '@/helpers';
import { notify } from '@/helpers/toast';
import { flatpickerConfig } from '../FlatPickr/flatpicker.constants';
import FlatPickr from '../FlatPickr/FlatPickr.vue';
import CheckboxField from '../forms/fields/CheckboxField.vue';
import InputField from '../forms/fields/InputField.vue';
import SelectField from '../forms/fields/SelectField.vue';
import Label from '../forms/Label.vue';

import type { IOrderQuote, IOrderService } from 'shared/types';

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  quote: {
    type: [Object, null] as PropType<IOrderQuote | null>,
    default: () => null
  }
});

const emit = defineEmits(['modal-close', 'modal-submit']);
const orderStore = useOrderStore();
const orderId = computed(() => orderStore.order?.id);
const selectedOption = ref('');
const selectedUom = ref();
const typeSpecific = ref(false);
const orderServices: Ref<IOrderService[]> = ref([]);
const mockNewService = {
  id: getRandomId(),
  name: '',
  comment: '',
  quantity_value: null,
  applies_on_arrival: false,
  applies_on_departure: false,
  is_arr_available: true,
  is_dep_available: true,
  is_allowed_quantity_selection: false,
  is_allowed_free_text: false
};
const userService = ref([{ ...mockNewService }]);
const displayServices = computed(() => [...userService.value]);
const aircrafts = computed(() => orderStore.order?.tails ?? []);
const activeAircraftIndex = ref(0);

const newServices: Ref<Array<any>> = ref([]);

const toDateTime = ref({
  date: new Date(new Date().getTime() + 48 * 60 * 60 * 1000).toLocaleDateString('en-CA'),
  time: '',
  timezone: 'Local'
});

const target = ref(null);

const { data: fetchedOrderServices } = useQueryOrderServices(orderId, {
  enabled: props.isOpen
});

const onValidate = async () => {
  const isValid = true; // Replace with validation if necessary
  if (!isValid) {
    return notify('Error while submitting, form is not valid!', 'error');
  } else {
    emit('modal-submit');
    emit('modal-close');
  }
};

const addNewService = async () => {
  newServices.value.push({
    ...mockNewService
  });
};

const changeTab = (index: number) => {
  activeAircraftIndex.value = index;
};

watch(
  () => fetchedOrderServices.value,
  (data) => {
    orderServices.value = data ? [...orderServices.value, ...toRaw(data)] : [];
  }
);
</script>

<style lang="scss">
.edit-quote-modal {
  .order-modal-header {
    color: rgba(39, 44, 63, 1);
    font-size: 18px;
    font-weight: 600;
    padding: 1.25rem 1.5rem 1.25rem 1.5rem;
    border-bottom: 1px solid rgba(223, 226, 236, 1);
  }

  &-tabs {
  }

  &-tab {
    color: rgba(82, 90, 122, 1);
    font-weight: 500;
    font-size: 15px;
    cursor: pointer;
    &-active {
      color: rgba(21, 28, 53, 1);
      border-bottom: 3px solid rgba(125, 148, 231, 1);
    }
  }

  .modal-button {
    display: flex;
    flex-shrink: 0;
    background-color: rgb(81 93 138);
    padding: 0.5rem;
    padding-left: 1rem;
    padding-right: 1rem;
    color: rgb(255 255 255);
    border-radius: 0.5rem;
    border-color: transparent;

    &.icon {
      background-color: rgba(240, 242, 252, 1);
      color: rgb(81 93 138);
      padding: 0.75rem;
      border-radius: 0.75rem;
      height: 100%;
    }
  }
  .button-cancel-service {
    background-color: rgba(255, 255, 255, 1) !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
    img {
      filter: brightness(0) saturate(100%) invert(35%) sepia(15%) saturate(1184%) hue-rotate(190deg)
        brightness(98%) contrast(92%);
    }
  }
  .el-border {
    border-right: 1px solid rgb(223, 226, 236);

    &-light {
      border-right: 1px solid theme('colors.dark-background');
    }
  }
  .order-modal-container {
    width: 45rem;
  }
  &-wrap {
    background-color: #eff1f6;
  }
  .handling-step-content {
    border: 1px solid #dfe2ec;
    border-radius: 0.5rem;
    overflow: hidden;
    background-color: #ffffff;
  }
}
</style>
