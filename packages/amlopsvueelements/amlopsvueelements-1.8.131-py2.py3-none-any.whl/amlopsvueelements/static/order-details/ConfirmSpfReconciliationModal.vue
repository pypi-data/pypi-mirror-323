<template>
  <div v-if="props.isOpen" class="order-modal">
    <div class="order-modal-wrapper">
      <div ref="target" class="order-modal-container">
        <div class="order-modal-body">
          <OrderForm add-default-classes is-modal>
            <template #header>
              <div class="header w-full flex justify-between">
                <div class="text-[1.25rem] font-medium text-grey-1000">
                  Confirm SPF Reconciliation
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
                <div v-if="isCreateStep" class="create-form-wrapper">
                  <div class="create-form-header">
                    <p class="create-form-header-title">New Tail Number</p>
                    <Button
                      class="button cancel-button items-center gap-2"
                      @click="() => (isCreateStep = false)"
                    >
                      <img width="12" height="12" src="../../assets/icons/cross.svg" alt="delete" />
                      Cancel
                    </Button>
                  </div>
                  <InputField v-model="form.asn" label-text="ASN" placeholder="Enter ASN" />
                  <InputField
                    v-model="form.registration"
                    label-text="Registration"
                    placeholder="Enter registration"
                    :required="true"
                    :is-validation-dirty="v$?.$dirty"
                    :errors="v$?.registration?.$errors"
                  />
                  <SelectField
                    v-model="form.aircraftType"
                    :required="true"
                    label-text="Aircraft Type"
                    placeholder="Aircraft Type"
                    :options="[]"
                    :is-validation-dirty="v$?.$dirty"
                    :errors="v$?.aircraftType?.$errors"
                  />
                  <InputField
                    v-model="form.paxSeats"
                    label-text="Pax Seats"
                    placeholder="Enter Pax Seats"
                  />
                </div>
                <div v-if="!isCreateStep" class="flex gap-[12px] align-center mb-[1rem]">
                  <SelectField
                    v-model="form.tailNumber"
                    :required="true"
                    class="mb-0"
                    label-text="Select / Verify Tail Number"
                    placeholder="Please select Tail Number"
                    label="display"
                    :options="tailNumberOptions"
                    :is-validation-dirty="v$?.$dirty"
                    :errors="v$?.tailNumber?.$errors"
                  />
                  <button class="button button-create" @click.stop="onClickCreate">Create</button>
                </div>
                <FileField
                  v-model="form.spfFile"
                  label-text="Upload Signed SPF File"
                  class="mb-[1rem]"
                  :error="unref(v$?.spfFile?.$errors?.[0]?.$message)"
                  @change="onChangeFile"
                />
                <InfoAlert
                  title="By clicking ‘Confirm’ you agree to lock the SPF as reconciled"
                  subtitle="This action is not reversible"
                />
              </div>
            </template>
          </OrderForm>
        </div>
        <div class="order-modal-footer">
          <Loading v-if="false" class="mr-4" />
          <button class="modal-button cancel" @click.stop="emit('modal-close')">Close</button>
          <button class="modal-button submit" @click.stop="onValidate()">Confirm</button>
        </div>
      </div>
    </div>
    <ConfirmationModal
      :is-open="isConfirmModalOpen"
      title="Please confirm you wish to lock the SPF as reconciled."
      subtitle="This action is not reversible."
      confirm-button="Confirm"
      cancel-button="Close"
      @modal-close="closeConfirmationModal"
      @modal-confirm="onSubmit"
    />
  </div>
</template>

<script lang="ts" setup>
import { computed, ref, unref, watch } from 'vue';
import { useQueryClient } from '@tanstack/vue-query';
import { useVuelidate } from '@vuelidate/core';
import { required, requiredIf } from '@vuelidate/validators';
import { Button } from 'shared/components';
import { useOrderStore } from '@/stores/useOrderStore';
import OrderForm from '@/components/forms/OrderForm.vue';
import { notify } from '@/helpers/toast';
import { InfoAlert } from '../datacomponent';
import FileField from '../forms/fields/FileField.vue';
import InputField from '../forms/fields/InputField.vue';
import SelectField from '../forms/fields/SelectField.vue';
import Loading from '../forms/Loading.vue';
import ConfirmationModal from './ConfirmationModal.vue';

import type { IAircraft } from 'shared/types';

type TailNumberOption = { id: IAircraft['id']; display: string };

type FormValues = {
  asn: string;
  registration: string;
  aircraftType: null;
  paxSeats: string;
  tailNumber: TailNumberOption | null;
  spfFile: File | null;
};

const props = defineProps({
  isOpen: Boolean
});

const emit = defineEmits(['modal-close', 'modal-submit']);

const queryClient = useQueryClient();
const orderStore = useOrderStore();

const target = ref(null);
const isConfirmModalOpen = ref(false);
const isCreateStep = ref(false);

const form = ref<FormValues>({
  asn: '',
  registration: '',
  aircraftType: null,
  paxSeats: '',
  tailNumber: null,
  spfFile: null
});

const validationRules = () => {
  return {
    registration: {
      requiredIf: requiredIf(() => !isCreateStep.value)
    },
    aircraftType: {
      requiredIf: requiredIf(() => !isCreateStep.value)
    },
    tailNumber: {
      requiredIf: requiredIf(() => !isCreateStep.value)
    },
    spfFile: { required }
  };
};

const v$ = ref(useVuelidate(validationRules(), form));

const orderId = computed(() => orderStore.orderId);
const isOpen = computed(() => props.isOpen);
const order = computed(() => orderStore.order);
const tailNumberOptions = computed(() => {
  return (
    order.value?.tails?.map((tail) => ({
      id: tail.id,
      display: tail.tail_number?.full_repr ?? ''
    })) ?? []
  );
});
const selectedTailNumber = ref<{ id: IAircraft['id']; display: string } | undefined>(
  tailNumberOptions.value ? tailNumberOptions.value[0] : undefined
);

const closeConfirmationModal = () => {
  isConfirmModalOpen.value = false;
};

const onClickCreate = () => {
  isCreateStep.value = !isCreateStep.value;
};

const onChangeFile = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  form.value.spfFile = file ?? null;
};

const onValidate = async () => {
  const isValid = await v$?.value?.$validate();

  if (!isValid) {
    return notify('Error while submitting, form is not valid!', 'error');
  } else {
    isConfirmModalOpen.value = true;
  }
};

const onSubmit = async () => {
  isConfirmModalOpen.value = false;

  if (!selectedTailNumber.value) return;

  // TODO: Add mutation when BE is ready
};

watch(tailNumberOptions, (options) => {
  form.value.tailNumber = options?.length === 1 ? options[0] : null;
});
</script>

<style scoped lang="scss">
.order-modal-footer {
  align-items: center;
  flex: 0 0 72px;
  min-height: 72px;

  .modal-button {
    max-height: 44px;
  }
}
.form-body-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;

  .button-create {
    align-self: flex-end;
    height: 40px;
    max-height: 40px;
  }

  .create-form-wrapper {
    border: 1px solid #dfe2ec;
    border-radius: 6px;
    margin: -4px -16px 24px -16px;
    padding: 12px 16px;

    .create-form-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      height: 40px;

      .create-form-header-title {
        font-size: 1rem;
        font-weight: 600;
        line-height: 1.5rem;
        color: theme('colors.base.800');
        margin: 0;
      }

      .cancel-button {
        border: none !important;
        background-color: #fe62621f !important;
        max-height: 40px;
      }
    }
  }
}
</style>
