<template>
  <div v-if="isOpen" class="order-modal request-ground-handling-modal">
    <div class="order-modal-wrapper">
      <div class="order-modal-container">
        <div class="order-modal-body">
          <OrderForm add-default-classes is-modal>
            <template #header>
              <div class="header w-full flex justify-between">
                <div class="text-[1.25rem] font-medium text-grey-1000">Request Ground Handling</div>
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
                <div class="flex w-full gap-3">
                  <div class="flex gap-[12px] align-center mb-[1rem] w-6/12">
                    <SelectField
                      v-model="recipients"
                      label-text="Recipients"
                      label="display"
                      placeholder="Choose Recipients"
                      class="mb-0"
                      :options="recipientsOptions ?? []"
                      :required="true"
                      :multiple="true"
                      :errors="errors.recipients"
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
                    class="w-6/12"
                    label-text="From"
                    :required="true"
                    :options="[userEmail, 'fuelteam@amlglobal.net']"
                    :errors="errors.from"
                  />
                </div>

                <InputField
                  v-model="subject"
                  class="w-full"
                  label-text="Subject"
                  placeholder="Please enter subject"
                />
                <Label label-text="Body Text"></Label>
                <Editor @update:value="onEditorUpdate" />
                <div class="flex w-full mb-[0.75rem]"></div>
                <!-- TO DO Remove after editor complete -->
                <span class="text-subtitle">Email content preview (dev only)</span>
                <div v-html="editorValue"></div>
                <Label label-text="Attachments" :required="false"></Label>
                <div v-if="isLoadingClientDocuments"><Loading /></div>
                <div v-else-if="clientDocuments?.length">
                  <div v-for="doc in clientDocuments" :key="doc.document_type">
                    <div
                      v-if="doc.document_type in CLIENT_DOCUMENT_TYPE_MAP_REVERSE"
                      class="flex items-start justify-start pb-[0.75rem]"
                    >
                      <CheckboxField
                        v-model="docs[CLIENT_DOCUMENT_TYPE_MAP_REVERSE[doc.document_type]]"
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
import { useUserStore } from '@/stores/useUserStore';
import OrderForm from '@/components/forms/OrderForm.vue';
import { useMutationSendSupplierOrderRequest } from '@/services/mutations/order';
import { useQueryOrderClientDocuments, useQueryRecipients } from '@/services/queries';
import { getAmlCompanyOption, getRecipientOptions } from '@/helpers/companies';
import {
  CLIENT_DOCUMENT_TYPE_MAP_REVERSE,
  getInitialClientDocumentTypes
} from '@/helpers/documents';
import { notify } from '@/helpers/toast';
import Editor from '../datacomponent/Editor.vue';
import CheckboxField from '../forms/fields/CheckboxField.vue';
import InputField from '../forms/fields/InputField.vue';
import SelectField from '../forms/fields/SelectField.vue';
import Label from '../forms/Label.vue';

import type { IClientQuoteRecipient } from 'shared/types';

const props = defineProps({
  isOpen: Boolean,
  organisationId: {
    type: Number,
    default: 0
  }
});

const emit = defineEmits(['modal-close', 'modal-submit']);

const orderStore = useOrderStore();
const userStore = useUserStore();

const queryClient = useQueryClient();

const userEmail = computed(() => userStore.user?.details?.contact_email ?? '');
const recipients = ref<IClientQuoteRecipient[]>([]);
const company = ref<{ id: number; display: string } | undefined>(
  orderStore?.order?.aml_selling_company
    ? getAmlCompanyOption(orderStore.order.aml_selling_company)
    : undefined
);
const from = shallowRef(userEmail.value);
const subject = shallowRef('');
const supplierNote = shallowRef('');
const docs = ref(getInitialClientDocumentTypes());
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

const editorValue: Ref<string | null> = ref('');

const replaceClassesWithStyles = (element: HTMLElement) => {
  const stylesMap = {
    'format-bold': 'font-weight: 700;',
    'format-italic': 'font-style: italic;',
    'format-underline': 'text-decoration: underline;',
    'format-strikethrough': 'text-decoration: line-through;',
    'format-superscript': 'vertical-align: super;',
    'format-subscript': 'vertical-align: sub;',
    'format-text-transform': 'text-transform: uppercase;',
    'format-text-inline': 'display: inline;',
    'format-text-block': 'display: block;',
    'format-align-left': 'text-align: left;',
    'format-align-center': 'text-align: center;',
    'format-align-right': 'text-align: right;',
    'format-align-justify': 'text-align: justify;',
    'resize-handle': 'display:none;'
  };

  const tagStylesMap = {
    table:
      'margin-top: 1rem; margin-bottom: 1rem; width: 100%; border: 1px solid #e0e0e0; box-shadow: 0 2px 4px #0000001a; background-color: #fff;',
    th: 'position: relative; min-width: 100px; border-width: 1px; border-color: rgb(209 213 219 / var(--tw-border-opacity, 1)); padding: 0.5rem; height: 24px; cursor: text; transition: background-color 0.2s ease;',
    td: 'position: relative; min-width: 100px; border-width: 1px; border-color: rgb(209 213 219 / var(--tw-border-opacity, 1)); padding: 0.5rem; height: 24px; cursor: text; transition: background-color 0.2s ease;'
  };

  element.querySelectorAll('*').forEach((child) => {
    for (const [className, style] of Object.entries(stylesMap)) {
      if (child.classList.contains(className)) {
        child.setAttribute('style', (child.getAttribute('style') || '') + style);
        child.classList.remove(className);
      }
      const tagName = child.tagName.toLowerCase();
      if (!(tagStylesMap as any)[tagName]) return;
      const currentStyle = child.getAttribute('style') || '';
      const newStyles = (tagStylesMap as any)[tagName]
        .split(';')
        .filter(Boolean)
        .filter((style: string) => !currentStyle.includes(style))
        .join('; ');

      if (newStyles) {
        child.setAttribute(
          'style',
          `${currentStyle}${currentStyle && newStyles ? '; ' : ''}${newStyles}`
        );
      }
    }
  });
};

const onEditorUpdate = (value: string) => {
  const html = document.createElement('div');
  html.innerHTML = value;
  replaceClassesWithStyles(html);
  // console.log(html.innerHTML);
  editorValue.value = html.innerHTML;
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
          sender: from.value,
          subject: subject.value,
          note: supplierNote.value,
          attachments: []
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

const { data: clientDocuments, isLoading: isLoadingClientDocuments } =
  useQueryOrderClientDocuments(orderId);

const { mutate: sendSupplierOrderRequestMutation, isPending: isSending } =
  useMutationSendSupplierOrderRequest();

const recipientsOptions = computed(() => getRecipientOptions(recipientsData.value?.recipients));

// const onAddRecipient = () => {
//   redirectToURL(`/ops/organisation/${props.organisationId}/contact_details/create/`);
// };

const validate = () => {
  errors.value = {
    company: company.value ? '' : 'Please select a company',
    recipients: recipients.value?.length ? '' : 'Please select at least one recipient',
    from: from.value ? '' : 'Please select a sender'
  };
};

onBeforeMount(() => {
  if (orderStore?.order) {
    const arrivalDateText = orderStore?.order?.gh_order?.arrival_datetime_utc?.split(' ')[0];
    const departureDateText = orderStore?.order?.gh_order?.departure_datetime_utc?.split(' ')[0];
    const dateTextGh = `${arrivalDateText} / ${departureDateText}`;
    const callsignText = orderStore?.order?.callsign;
    const codesText = `${orderStore?.order?.location?.airport_details?.icao_code ?? 'N/A'} / ${
      orderStore?.order?.location?.airport_details?.iata_code ?? 'N/A'
    }`;
    subject.value = `Ground Handling Request - ${codesText} - ${callsignText} - ${dateTextGh}`;
  }
});

watch([company, recipients, from], () => {
  validate();
});
</script>

<style scoped lang="scss">
.request-ground-handling-modal {
  .order-modal-container {
    width: 1024px;
  }
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
