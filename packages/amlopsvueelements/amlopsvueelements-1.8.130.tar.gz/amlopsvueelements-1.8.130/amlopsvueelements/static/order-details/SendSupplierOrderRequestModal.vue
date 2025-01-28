<template>
  <div v-if="isOpen" class="order-modal send-supplier-request-modal">
    <div class="order-modal-wrapper">
      <div class="order-modal-container">
        <div class="order-modal-body">
          <OrderForm add-default-classes is-modal>
            <template #header>
              <div class="header w-full flex justify-between">
                <div class="text-[1.25rem] font-medium text-grey-1000">
                  {{
                    props.isUpdate
                      ? 'Send Supplier Fuel Order Update Request'
                      : 'Send Supplier Order Request'
                  }}
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
                <SelectField
                  v-model="company"
                  label-text="AML Buying Company"
                  label="display"
                  placeholder="Company"
                  :required="true"
                  :options="companiesOptions ?? []"
                />
                <div class="flex gap-[12px] align-center mb-[1rem]">
                  <SelectField
                    v-model="recipients"
                    label-text="Recipients"
                    label="display"
                    placeholder="Choose Recipients"
                    class="mb-0"
                    :options="recipientsOptions ?? []"
                    :required="true"
                    :multiple="true"
                  />
                  <!-- TODO: Uncomment once Add Additional Contact Detail page by @Denis Verbin is ready -->
                  <!-- <div class="add-recipient-btn">
                    <img
                      width="12"
                      height="12"
                      src="../../assets/icons/plus.svg"
                      alt="comment"
                      @click="onAddRecipient"
                    />
                  </div> -->
                </div>
                <SelectField
                  v-model="from"
                  label-text="From"
                  label="address"
                  :required="true"
                  :options="fromOptions"
                />
                <InputField
                  v-model="subject"
                  class="w-full"
                  label-text="Subject"
                  placeholder="Please enter subject"
                />
                <TextareaField
                  v-model="supplierNote"
                  class="w-full"
                  label-text="Supplier Note"
                  placeholder="Please enter supplier note"
                />
                <Label label-text="Attachments" :required="false"></Label>
                <div v-if="isLoadingClientDocuments"><Loading /></div>
                <div v-else-if="clientDocuments?.length">
                  <div v-for="doc in docs" :key="doc.document_type">
                    <div
                      v-if="doc.document_type in CLIENT_DOCUMENT_TYPE_MAP_REVERSE"
                      class="flex items-start justify-start pb-[0.75rem]"
                    >
                      <CheckboxField
                        v-model="doc.checked"
                        class="mb-0 mt-[2px] mr-[0.25rem]"
                        :size="'20px'"
                      />
                      <div class="checkbox-text flex flex-col">
                        <p class="text-base whitespace-nowrap font-semibold text-main">
                          {{ doc.document_type }}
                        </p>
                        <p class="text-sm whitespace-nowrap text-subtitle">
                          {{ doc.document_name }}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </OrderForm>
        </div>
        <div class="order-modal-footer items-center">
          <Loading v-if="isSending" class="mr-4" />
          <button class="modal-button cancel" @click.stop="emit('modal-close')">Cancel</button>
          <button
            class="modal-button submit"
            :disabled="hasErrors || isSending"
            @click.stop="onSubmit()"
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed, onBeforeMount, type Ref, ref, shallowRef, watch } from 'vue';
import { useQueryClient } from '@tanstack/vue-query';
import { Loading } from 'shared/components';
import { useOrderStore } from '@/stores/useOrderStore';
import OrderForm from '@/components/forms/OrderForm.vue';
import { useMutationSendSupplierOrderRequest } from '@/services/mutations/order';
import { useQueryOrderClientDocuments, useQueryRecipients } from '@/services/queries';
import { useQueryAmlBuyingCompanies } from '@/services/queries/organisations';
import { redirectToURL } from '@/helpers';
import {
  getAmlCompanyOption,
  getPreselected,
  getPreselectedArray,
  getRecipientOptions,
  mapRecipientDisplay
} from '@/helpers/companies';
import { CLIENT_DOCUMENT_TYPE_MAP_REVERSE } from '@/helpers/documents';
import { notify } from '@/helpers/toast';
import CheckboxField from '../forms/fields/CheckboxField.vue';
import InputField from '../forms/fields/InputField.vue';
import SelectField from '../forms/fields/SelectField.vue';
import TextareaField from '../forms/fields/TextareaField.vue';
import Label from '../forms/Label.vue';

import type { IClientDocument, IClientQuoteRecipient, IClientQuoteSender } from 'shared/types';

const props = defineProps({
  isOpen: Boolean,
  isUpdate: {
    type: Boolean,
    default: false
  },
  organisationId: {
    type: Number,
    default: 0
  }
});

const emit = defineEmits(['modal-close', 'modal-submit']);

const orderStore = useOrderStore();

const queryClient = useQueryClient();

const company = ref<{ id: number; display: string } | undefined>(
  orderStore?.order?.aml_selling_company
    ? getAmlCompanyOption(orderStore.order.aml_selling_company)
    : undefined
);
const subject = shallowRef('');
const supplierNote = shallowRef('');
const docs: Ref<Array<IClientDocument & { checked: boolean }>> = ref([]);
const errors = ref({
  company: '',
  recipients: '',
  from: ''
});

const isOpen = computed(() => props.isOpen);
const hasErrors = computed(() => Object.values(errors.value).some(Boolean));
const orderId = computed(() => orderStore.orderId);
const recipientsQueryParam = computed(() => ({
  orderId: orderId.value,
  recipientType: 'supplier' as const
}));

const mapDocsValue = (docs: Array<IClientDocument & { checked: boolean }>) => {
  return docs
    .filter((doc) => doc.checked)
    .map((doc) => ({
      pk: doc.pk,
      category: doc.document_category
    }));
};

const onSubmit = async () => {
  validate();

  if (hasErrors.value || !company.value || !recipients.value.length || !from.value) {
    return notify('Error while submitting, please fill the required fields ', 'error');
  } else {
    await sendSupplierOrderRequestMutation(
      {
        orderId: orderId.value,
        payload: {
          recipients: recipients.value.map((recipient) => ({
            name: recipient.name,
            address: recipient.address,
            recipient_type: recipient.recipient_type
          })),
          aml_buying_company: company.value?.id,
          sender: from.value.address,
          subject: subject.value,
          note: supplierNote.value,
          attachments: mapDocsValue(docs.value),
          update: props.isUpdate
        }
      },
      {
        onSuccess: () => {
          notify('Supplier order request sent successfully!', 'success');
          queryClient.invalidateQueries({ queryKey: ['orderStatus', orderId] });
          emit('modal-close');
          emit('modal-submit');
        }
      }
    );
  }
};

const { data: recipientsData } = useQueryRecipients(recipientsQueryParam);

const { data: amlBuyingCompanies } = useQueryAmlBuyingCompanies({
  enabled: isOpen
});

const { data: clientDocuments, isLoading: isLoadingClientDocuments } =
  useQueryOrderClientDocuments(orderId);

const { mutate: sendSupplierOrderRequestMutation, isPending: isSending } =
  useMutationSendSupplierOrderRequest();

const companiesOptions = computed(() => {
  return amlBuyingCompanies.value?.map(getAmlCompanyOption);
});

const fromOptions = computed(() => recipientsData?.value?.senders ?? []);
const recipientsOptions = computed(
  () => getRecipientOptions(recipientsData.value?.recipients) as IClientQuoteRecipient[]
);
const from: Ref<IClientQuoteSender | null> = ref(getPreselected(fromOptions?.value) ?? null);
const recipients = ref<IClientQuoteRecipient[]>([]);

const onAddRecipient = () => {
  redirectToURL(`/ops/organisation/${props.organisationId}/contact_details/create/`);
};

const validate = () => {
  errors.value = {
    company: company.value ? '' : 'Please select a company',
    recipients: recipients.value?.length ? '' : 'Please select at least one recipient',
    from: from.value ? '' : 'Please select a sender'
  };
};

onBeforeMount(() => {
  if (orderStore?.order) {
    const dateText = orderStore?.order?.fulfilment_datetime_local_str?.split(' ')[0];
    // TODO: add type_designator after callsign: `$callsign ($type_designator)`
    const callsignText = orderStore?.order?.callsign;
    const codesText = `${orderStore?.order?.location?.airport_details?.icao_code ?? 'N/A'} / ${
      orderStore?.order?.location?.airport_details?.iata_code ?? 'N/A'
    }`;
    const subjectText = `AML Fuel Order Request for ${callsignText} - ${codesText} - ${dateText}`;
    subject.value = props.isUpdate ? `UPDATE - ${subjectText}` : subjectText;
  }
});

watch([company, recipients, from], () => {
  validate();
});

watch(fromOptions, (fromOptionsValue) => {
  if (fromOptionsValue) {
    const preSelected = getPreselected(fromOptionsValue);
    if (preSelected) from.value = preSelected;
  }
});

watch(recipientsOptions, (recipientsOptionsValue) => {
  recipients.value = getPreselectedArray(recipientsOptionsValue) ?? [];
});

watch(clientDocuments, (clientDocumentsValue) => {
  if (clientDocumentsValue) {
    docs.value = clientDocumentsValue.map((doc) => {
      return { ...doc, checked: false };
    });
  }
});
</script>

<style scoped lang="scss">
.send-supplier-request-modal {
  .form-body-wrapper {
    max-height: 500px;
  }
}

.add-recipient-btn {
  display: flex;
  flex: 0;
  align-items: center;
  align-self: flex-end;
  justify-content: center;
  cursor: pointer;
  border-radius: 8px;
  background: rgba(240, 242, 252, 1);
  min-width: 42px;
  min-height: 42px;

  img {
    filter: invert(40%) sepia(5%) saturate(4138%) hue-rotate(190deg) brightness(84%) contrast(85%);
  }
}
</style>
