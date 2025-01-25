<template>
  <div v-if="isOpen" class="order-modal add-document-modal">
    <div class="order-modal-wrapper">
      <div ref="target" class="order-modal-container">
        <div class="order-modal-body">
          <OrderForm add-default-classes :is-modal="true">
            <template #header>
              <div class="header w-full flex justify-between">
                <div class="text-[1.25rem] font-medium text-grey-1000">Add Document</div>
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
              <ScrollBar>
                <div class="form-body-wrapper">
                  <SelectField
                    v-model="entity"
                    label-text="Entity"
                    :disabled="isEntityDisabled"
                    required
                    placeholder=""
                    label="full_repr"
                    :options="entities"
                    :errors="errors.entity"
                  ></SelectField>
                  <SelectField
                    v-model="type"
                    label-text="Type"
                    required
                    placeholder=""
                    label="name"
                    :options="clientDocumentTypes"
                    :errors="errors.type"
                  ></SelectField>
                  <div class="flex items-end gap-[1rem] mb-[1rem] w-full">
                    <div class="flex flex-col">
                      <Label :required="false" label-text="Valid From" />
                      <FlatPickr v-model="date.from" placeholder="" :config="flatpickerConfig" />
                    </div>
                    <div class="flex flex-col">
                      <Label
                        :required="false"
                        label-text="Valid To"
                        :class="{ 'text-disabled': dateUFN }"
                      />
                      <FlatPickr
                        v-model="date.to"
                        :is-disabled="dateUFN"
                        placeholder=""
                        :config="flatpickerConfig"
                      />
                    </div>
                    <div class="flex items-center mb-[0.5rem]">
                      <CheckboxField v-model="dateUFN" :size="'24px'" class="mb-0 mr-[0.25rem]" />
                      <p class="text-base whitespace-nowrap">UFN</p>
                    </div>
                  </div>
                  <InputField
                    v-model="name"
                    required
                    class="w-full mb-[1rem]"
                    label-text="Name"
                    placeholder="Please enter name"
                    :errors="errors.name"
                  />
                </div>
                <div class="flex items-center justify-between mb-[0.75rem] gap-3">
                  <div class="flex items-center gap-3">
                    <button class="modal-button icon" @click="onFileInputClick()">
                      <img
                        height="20"
                        width="20"
                        :src="
                          file
                            ? getImageUrl('assets/icons/file.svg')
                            : getImageUrl('assets/icons/paperclip.svg')
                        "
                        alt="attachment"
                      />
                    </button>
                    <input
                      ref="fileInputAddDocument"
                      class="hidden"
                      type="file"
                      @change="onChangeFile($event)"
                    />
                    <p class="text-base whitespace-nowrap font-semibold text-main">
                      {{
                        (file! as File)?.name
                          ? (file! as File)?.name.split('.')[0].substring(0, 40) +
                            '.' +
                            (file! as File)?.name.split('.')[1]
                          : ' Select Document File'
                      }}
                    </p>
                  </div>
                  <div v-show="errors.file" class="ticket-error">
                    <span>{{ errors.file }}</span>
                  </div>
                  <div class="flex">
                    <img
                      v-if="file"
                      width="20"
                      height="20"
                      src="../../assets/icons/cross-red.svg"
                      alt="delete"
                      class="cursor-pointer"
                      @click="onDeleteFile()"
                    />
                  </div>
                </div>
              </ScrollBar>
            </template>
          </OrderForm>
        </div>
        <div class="order-modal-footer flex items-center">
          <Loading v-if="isSending" class="mr-4" />
          <button class="modal-button cancel" @click.stop="emit('modal-close')">Back</button>
          <button class="modal-button submit" @click.stop="onSubmit()">Create Document</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { type ComputedRef, type Ref, ref, shallowRef, watch } from 'vue';
import { computed } from 'vue';
import { useQueryClient } from '@tanstack/vue-query';
import { useOrderStore } from '@/stores/useOrderStore';
import OrderForm from '@/components/forms/OrderForm.vue';
import {
  type AddOrderDocumentRequest,
  useMutationAddOrderDocumentRequest
} from '@/services/mutations/order';
import { useQueryOrderClientDocumentTypes } from '@/services/queries';
import { getImageUrl } from '@/helpers';
import { notify } from '@/helpers/toast';
import { flatpickerConfig } from '../FlatPickr/flatpicker.constants';
import FlatPickr from '../FlatPickr/FlatPickr.vue';
import CheckboxField from '../forms/fields/CheckboxField.vue';
import InputField from '../forms/fields/InputField.vue';
import SelectField from '../forms/fields/SelectField.vue';
import Label from '../forms/Label.vue';
import Loading from '../forms/Loading.vue';
import ScrollBar from '../forms/ScrollBar.vue';

import type {
  IAircraft,
  IClient,
  ITailNumber,
  ITypeReference,
  SomeAreRequired
} from 'shared/types';

enum EntityType {
  Organisation = 'organisation',
  Aircraft = 'aircraft'
}

type Entity = (IClient & { type: EntityType }) | (ITailNumber & { type: EntityType });
type TailWithNumber = SomeAreRequired<IAircraft, 'tail_number'>;

const props = defineProps({
  isOpen: Boolean
});

const emit = defineEmits(['modal-close', 'modal-submit']);
const target = ref(null);

const orderStore = useOrderStore();
const order = computed(() => orderStore.order);
const orderId = computed(() => orderStore.order?.id);
const entities: ComputedRef<Array<Entity>> = computed(() => {
  if (order.value?.client == null) return [];

  const organisation = { ...order.value.client, type: EntityType.Organisation };

  if (!order.value?.tails || order.value?.tails?.length === 0) return [organisation];

  const tailsWithNumbers = order.value.tails.filter((el): el is TailWithNumber => !!el.tail_number);

  return [
    organisation,
    ...tailsWithNumbers.map((el) => ({ ...el.tail_number, type: EntityType.Aircraft }))
  ];
});
const isEntityDisabled = computed(() => !order.value?.tails?.length);
const entity: Ref<Entity | null> = ref(
  isEntityDisabled.value && order.value?.client
    ? { ...order.value.client, type: EntityType.Organisation }
    : null
);
const date = ref({
  from: '',
  to: ''
});
const dateUFN = shallowRef(false);
const name = shallowRef('');
const type: Ref<ITypeReference | null> = ref(null);
const file = ref(null);
const fileInputAddDocument = ref(null);
const enabled = ref(false);
const typesPayload = computed(() => {
  return {
    orderId: orderId.value ?? 0,
    entity_type: entity.value?.type ?? ''
  };
});
const errors = ref({
  type: '',
  entity: '',
  file: '',
  name: ''
});
const hasErrors = computed(() => Object.values(errors.value).some(Boolean));
const queryClient = useQueryClient();

const onChangeFile = (event: any) => {
  const fileData = event.target.files[0];
  if (fileData) {
    file.value = fileData;
  }
};

const onDeleteFile = () => {
  file.value = null;
  (fileInputAddDocument.value! as any).value = null;
};

const onFileInputClick = () => {
  (fileInputAddDocument.value! as HTMLElement).click();
};

const { data: clientDocumentTypes } = useQueryOrderClientDocumentTypes(typesPayload, {
  enabled,
  retry: false
});

const { mutate: addOrderDocumentMutation, isPending: isSending } =
  useMutationAddOrderDocumentRequest();

const refreshForm = () => {
  type.value = null;
  date.value = {
    from: '',
    to: ''
  };
  dateUFN.value = false;
  name.value = '';
  file.value = null;
  errors.value = {
    type: '',
    entity: '',
    file: '',
    name: ''
  };
};

const validate = () => {
  errors.value = {
    type: type.value ? '' : 'Please select a type',
    entity: entity.value ? '' : 'Please select an entity',
    name: name.value ? '' : 'Please enter file name',
    file: file.value ? '' : 'Please upload a file'
  };
};

const onSubmit = async () => {
  validate();
  if (hasErrors.value) {
    return notify('Error while submitting, please fill the required fields ', 'error');
  } else {
    const payload: AddOrderDocumentRequest['payload'] = {
      file: file.value!,
      name: name.value,
      valid_from: date.value.from,
      valid_to: date.value.to,
      type: type.value!.id,
      valid_ufn: dateUFN.value,
      is_organisation_doc: entity.value!.type === EntityType.Organisation
    };
    if (entity.value!.type === EntityType.Aircraft) {
      payload['aircraft_history'] = entity.value!.id;
      payload['description'] = name.value;
    }

    await addOrderDocumentMutation(
      {
        orderId: orderId.value!,
        payload
      },
      {
        onSuccess: () => {
          notify('Document created successfully!', 'success');
          queryClient.invalidateQueries({ queryKey: ['orderClientDocuments', orderId.value] });
          emit('modal-close');
          refreshForm();
        }
      }
    );
  }
};

watch(
  () => [props.isOpen, entity.value],
  ([isOpen, entity]) => {
    enabled.value = !!(isOpen && entity !== null);
  }
);

watch(
  () => dateUFN.value,
  (value) => {
    if (value) {
      date.value.to = '';
    }
  }
);

watch(entities, (entitiesValue) => {
  if (entitiesValue?.length === 1 && isEntityDisabled) entity.value = entitiesValue[0];
});
</script>

<style scoped lang="scss">
.add-document-modal {
  .modal-button {
    &.icon {
      background-color: rgba(240, 242, 252, 1);
      color: rgb(81 93 138);
      padding: 0.75rem;
      border-radius: 0.75rem;
      height: 100%;
    }
  }

  .ticket-error {
    font-size: 0.75rem;
    color: rgb(225, 29, 72);
  }
}
</style>
