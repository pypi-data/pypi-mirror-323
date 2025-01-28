<template>
  <div ref="header" class="order-header flex flex-col">
    <CancelOrderModal
      v-if="modal === 'cancel-order'"
      :is-open="modal === 'cancel-order'"
      @modal-close="closeModal"
    />
    <DeclineOrderModal
      :is-open="modal === 'decline'"
      :order-id="orderId"
      @modal-close="closeModal"
    />
    <SendViaEmailModal
      ref="emailInput"
      :is-open="modal === 'send-email'"
      name="email-modal"
      @modal-close="closeModal()"
    />
    <SendSupplierOrderRequestModal
      v-if="modal === 'supplier-order-request' || modal === 'supplier-order-request-update'"
      :is-open="modal === 'supplier-order-request' || modal === 'supplier-order-request-update'"
      :is-update="modal === 'supplier-order-request-update'"
      :organisation-id="order?.client?.id"
      name="request-modal"
      @modal-close="closeModal"
    />
    <SendClientFuelReleaseModal
      v-if="modal === 'client-fuel-release'"
      ref="clientInput"
      :is-open="modal === 'client-fuel-release'"
      :organisation-id="order?.client?.id"
      name="client-modal"
      @modal-close="closeModal()"
    />
    <MarkNoUpliftModal
      ref="markInput"
      :is-open="modal === 'mark-no-uplift'"
      name="mark-modal"
      @modal-close="closeModal()"
    />
    <NoServicingTakenModal
      :is-open="modal === 'no-servicing-taken'"
      name="no-servicing-taken"
      @modal-close="closeModal"
    />
    <ConfirmGroundHandlingModal
      :is-open="modal === 'confirm-ground-handling'"
      name="confirm-ground-handling"
      @modal-close="closeModal"
    />
    <ConfirmSpfReconciliationModal
      :is-open="modal === 'confirm-spf-reconciliation'"
      name="confirm-spf-reconciliation"
      @modal-close="closeModal"
    />
    <ConfirmSupplierOrderModal
      ref="markInput"
      :is-open="modal === 'confirm-supplier-order'"
      :organisation-id="order?.client?.id"
      name="confirm-modal"
      @modal-close="closeModal()"
    />
    <SubmitDeliveryTicketDetailsModal
      ref="markInput"
      :is-open="modal === 'submit-delivery-ticket'"
      :organisation-id="order?.client?.id"
      name="confirm-modal"
      @modal-close="closeModal()"
    />
    <SupplierDeclinedOrderModal
      v-if="modal === 'supplier-declined-order'"
      :is-open="modal === 'supplier-declined-order'"
      :is-gh="isGh"
      @modal-close="closeModal({ disableRouteChange: true })"
    />
    <RequestGroundHandlingModal
      v-if="modal === 'request-ground-handling'"
      :is-open="modal === 'request-ground-handling'"
      @modal-close="closeModal()"
    />
    <WaitingOnPricingModal
      v-if="modal === 'waiting-on-pricing'"
      :is-open="modal === 'waiting-on-pricing'"
      @modal-close="closeModal()"
    />
    <OldSystemDetailsModal
      v-if="modal === 'details-old-system'"
      :is-open="modal === 'details-old-system'"
      @modal-close="closeModal()"
    />
    <div
      class="order-status flex w-full justify-between items-center mb-4 px-[1rem] pt-[0.5rem] pb-[0.6rem] overflow-auto"
      :style="{
        // eslint-disable-next-line prettier/prettier
        background: `repeating-linear-gradient(45deg,${changeColorAlpha(
          getColor(),
          0.1
        )},${changeColorAlpha(getColor(), 0.1)} 10px,rgb(255, 255, 255) 0,rgb(255, 255, 255) 20px)`,
        color: getTextColor(),
        'border-top': `4px solid ${getColor()}`,
        'border-bottom': `1px solid ${changeColorAlpha(getColor(), 0.2)}`
      }"
    >
      <div v-if="isStatus" class="status flex py-[0.25rem]" :style="{ color: getTextColor() }">
        <span>{{ orderStatus?.status?.status_details?.name?.toUpperCase() }}</span>
      </div>
      <div class="status-buttons flex gap-3">
        <Loading v-if="isLoading" class="mr-2" />
        <Button
          v-if="orderStatus?.progress?.globals?.is_cancel_order_available"
          class="button cancel-button items-center gap-2"
          @click="openModal('cancel-order')"
        >
          <img width="12" height="12" src="../../assets/icons/cross.svg" alt="delete" />
          Cancel Order
        </Button>
        <Button
          v-if="orderStatus?.progress?.globals?.is_reinstate_order_available"
          class="button items-center"
          @click="onReinstateOrder"
        >
          Reinstate Order
        </Button>
        <div v-if="currentStep === 1 && isFuel" class="status-buttons flex gap-3">
          <Button
            v-if="isRefreshSupplierPricingButtonShown"
            class="button"
            :disabled="!(orderStatus?.progress as IFuelProgress)?.pricing?.is_editable"
            @click="onRefreshSupplierPricing"
          >
            <div class="el flex">Refresh Supplier Pricing</div>
          </Button>
          <Button
            v-if="(orderStatus?.progress as IFuelProgress)?.pricing?.is_send_client_quote_available"
            :disabled="!(orderStatus?.progress as IFuelProgress)?.pricing?.is_editable"
            class="button"
            @click="openModal('send-email')"
          >
            <div class="el flex gap-2">Send Client Quote</div>
          </Button>
          <Button
            v-if="(orderStatus?.progress as IFuelProgress)?.pricing?.is_waiting_on_pricing_available"
            :disabled="!(orderStatus?.progress as IFuelProgress)?.pricing?.is_editable"
            class="button button-yellow"
            @click="openModal('waiting-on-pricing')"
          >
            <div class="el flex gap-2">Waiting on Pricing</div>
          </Button>
          <Button
            v-if="(orderStatus?.progress as IFuelProgress)?.pricing?.is_proceed_to_compliance_available"
            class="button button-green flex items-center gap-2"
            :disabled="!orderPricing?.supplier_id || !(orderStatus?.progress as IFuelProgress)?.pricing?.is_editable"
            @click="onProceedToCompliance"
          >
            {{ isQuote ? 'Convert to Order' : 'Proceed to Compliance' }}
          </Button>
        </div>
        <div v-if="currentStep === 1 && isGh" class="status-buttons flex gap-3">
          <Button
            class="button button-green flex items-center gap-2"
            :disabled="!orderStore.order?.gh_order?.ground_handler"
            @click="onProceedToCompliance"
          >
            Proceed to Servicing
          </Button>
        </div>
        <div v-if="currentStep === 2 && isFuel" class="status-buttons flex gap-3">
          <Button
            v-if="
              !isDeclined && !!proceedComplianceData?.action_buttons?.decline_order_button_visible
            "
            :disabled="!(orderStatus?.progress as IFuelProgress)?.compliance?.is_editable"
            class="button cancel-button items-center gap-2"
            @click="openModal('decline')"
          >
            <img width="12" height="12" src="../../assets/icons/cross.svg" alt="delete" />
            Decline Order
          </Button>
          <Button
            v-if="proceedComplianceData?.action_buttons?.approve_order_button_visible"
            :disabled="isFetchingApproveOrder || !(orderStatus?.progress as IFuelProgress)?.compliance?.is_editable"
            class="button button-green flex items-center gap-2"
            @click="onApproveOrder"
          >
            <img src="../../assets/icons/check.svg" alt="approve" />
            Approve Order
          </Button>
          <Button
            v-if="proceedComplianceData?.compliance_status?.status === 'Auto-Approved'"
            class="button button-green flex items-center gap-2"
            :disabled="!(orderStatus?.progress as IFuelProgress)?.compliance?.is_editable"
            @click="onApproveOrder"
          >
            Proceed to Order
          </Button>
        </div>
        <div v-if="currentStep === 2 && isGh" class="status-buttons flex gap-3">
          <Button
            v-if="supplierStatusId === 'supplier_order_placed'"
            class="button cancel-button items-center gap-2"
            @click="openModal('supplier-declined-order')"
          >
            Supplier Declined Order
          </Button>
          <Button
            v-if="(orderStatus?.progress as IGhProgress)?.servicing?.is_no_servicing_btn_available"
            class="button cancel-button items-center gap-2"
            @click="openModal('no-servicing-taken')"
          >
            <img width="12" height="12" src="../../assets/icons/cross.svg" alt="delete" />
            No Servicing Taken
          </Button>
          <Button
            v-if="true || supplierStatusId === 'ready_to_order'"
            class="button"
            @click="openModal('request-ground-handling')"
          >
            <div class="el flex gap-2">Request Ground Handling</div>
          </Button>
          <Button
            v-if="supplierStatusId === 'supplier_order_placed'"
            class="button button-green items-center gap-2"
            @click="openModal('confirm-ground-handling')"
          >
            Confirm Ground Handling
          </Button>
        </div>
        <div v-if="currentStep === 3" class="status-buttons flex gap-3">
          <Button
            v-if="(orderStatus?.progress as IFuelProgress)?.order?.is_send_supplier_order_update_available"
            :disabled="!(orderStatus?.progress as IFuelProgress)?.order?.is_editable"
            class="button"
            @click="openModal('supplier-order-request-update')"
          >
            Supplier Fuel Order Update
          </Button>
          <Button
            v-if="supplierStatusId === 'ready_to_order'"
            :disabled="!(orderStatus?.progress as IFuelProgress)?.order?.is_editable"
            class="button"
            @click="openModal('supplier-order-request')"
          >
            Send Supplier Order Request
          </Button>
          <Button
            v-if="(orderStatus?.progress as IFuelProgress)?.order?.is_send_client_fuel_release_available"
            class="button"
            :disabled="!(orderStatus?.progress as IFuelProgress)?.order?.is_editable"
            @click="openModal('client-fuel-release')"
          >
            Send Client Fuel Release
          </Button>
          <Button
            v-if="(orderStatus?.progress as IFuelProgress)?.order?.is_submit_delivery_ticket_available"
            class="button"
            :class="{ 'button-expired': isExpired }"
            @click="openModal('submit-delivery-ticket')"
          >
            {{ 'Submit Delivery Ticket Details' + (isExpired ? ' (Expired Order)' : '') }}
          </Button>
          <Button
            v-if="(orderStatus?.progress as IFuelProgress)?.order?.is_mark_as_non_uplift_available"
            :disabled="!(orderStatus?.progress as IFuelProgress)?.order?.is_editable"
            class="button cancel-button items-center gap-2"
            @click="openModal('mark-no-uplift')"
          >
            <img width="12" height="12" src="../../assets/icons/cross.svg" alt="delete" />
            Mark as No-Uplift
          </Button>
          <Button
            v-if="(orderStatus?.progress as IFuelProgress)?.order?.is_confirm_supplier_order_available"
            :disabled="!(orderStatus?.progress as IFuelProgress)?.order?.is_editable"
            class="button cancel-button items-center"
            @click="openModal('supplier-declined-order')"
          >
            Supplier Declined Order
          </Button>
          <Button
            v-if="(orderStatus?.progress as IFuelProgress)?.order?.is_confirm_supplier_order_available"
            :disabled="!(orderStatus?.progress as IFuelProgress)?.order?.is_editable"
            class="button button-green flex items-center gap-2"
            @click="openModal('confirm-supplier-order')"
          >
            <img src="../../assets/icons/check.svg" alt="approve" />
            Confirm Supplier Order
          </Button>
          <Button
            v-if="(orderStatus?.progress as IFuelProgress)?.order?.is_issue_fuel_release_available"
            class="button button-green flex items-center gap-2"
            :disabled="
              isFetchingGenerateSfFuelRelease || !(orderStatus?.progress as IFuelProgress)?.order?.is_editable
            "
            @click="onIssueFuelRelease"
          >
            Issue Fuel Release
          </Button>
          <Button
            class="button flex items-center"
            :disabled="!(orderStatus?.progress as IFuelProgress)?.order?.is_editable"
            @click="openModal('details-old-system')"
          >
            Details for Old System
          </Button>
        </div>
        <div v-if="currentStep === 3 && isGh" class="status-buttons flex gap-3">
          <Button
            class="button button-green items-center gap-2"
            @click="openModal('confirm-spf-reconciliation')"
          >
            Mark SPF as Reconciled
          </Button>
        </div>
      </div>
    </div>
    <div class="order-name-wrap mb-4 px-[1rem] flex flex-col">
      <div class="order-name-row flex gap-2 items-center">
        <div class="order-name">
          {{ order?.aml_order_number }}
        </div>
        <div
          v-if="order?.linked_order"
          class="order-linked flex items-center px-[0.5rem] gap-2 cursor-pointer"
          @click="redirectToLinkedOrder(order?.linked_order?.uri!)"
        >
          <img src="../../assets/icons/linked.svg" alt="linked" />
          <div class="order-linked-text">
            {{ order?.linked_order?.aml_order_number }}
          </div>
        </div>
        <Avatar
          v-if="order?.assigned_aml_person"
          :first-name="order?.assigned_aml_person?.details?.first_name"
          :last-name="order?.assigned_aml_person?.details?.last_name"
          :is-small="true"
        ></Avatar>
      </div>
      <div
        class="order-company cursor-pointer flex w-fit"
        @click="redirectToURL(order?.client?.url)"
      >
        {{ order?.client?.details?.registered_name }}
        <img
          width="12"
          height="12"
          src="../../assets/icons/chevron-right.svg"
          alt="warn"
          class="warn ml-[0.25rem]"
        />
      </div>
    </div>
    <div v-if="order?.type?.is_fuel" class="order-content flex pb-[1rem] px-[1rem] gap-2">
      <div class="order-content-col w-4/12 flex flex-col gap-1.5">
        <div
          v-if="!order?.fuel_order?.is_open_release"
          class="order-content-el flex gap-3 items-start"
        >
          <div class="order-content-header w-4/12">Uplift Time (UTC)</div>
          <div class="order-content-data w-8/12">
            {{
              fuelUplifts && fuelUplifts.length > 0
                ? toUTCdateTime(fuelUplifts[0].time_z)
                : order?.fulfilment_datetime
                ? order?.fulfilment_datetime_str
                : 'TBC'
            }}
          </div>
        </div>
        <div v-else class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-4/12">Release Start Date</div>
          <div class="order-content-data w-8/12">
            {{
              order?.fuel_order?.arrival_time_tbc
                ? order?.fuel_order?.arrival_datetime_utc
                : order?.fuel_order?.arrival_datetime_utc.slice(0, 10)
            }}
          </div>
        </div>
        <div class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-4/12">IPA</div>
          <div class="order-content-data w-8/12">
            <span
              :class="{ 'cursor-pointer': order?.fuel_order?.ipa }"
              @click="redirectToURL(order?.fuel_order?.ipa?.url)"
            ></span>
            {{ order?.fuel_order?.ipa?.full_repr ?? 'TBC' }}
            <img
              v-if="order?.fuel_order?.ipa"
              width="12"
              height="12"
              src="../../assets/icons/chevron-right.svg"
              alt="warn"
              class="warn cursor-pointer ml-[0.25rem]"
              @click="redirectToURL(order?.fuel_order?.ipa?.url)"
            />
          </div>
        </div>
        <div class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-4/12">Operator</div>
          <div class="order-content-data w-8/12">
            <span class="cursor-pointer" @click="redirectToURL(order?.operator?.url)">
              {{ order?.operator?.details?.registered_name }}</span
            >
            <img
              width="12"
              height="12"
              src="../../assets/icons/chevron-right.svg"
              alt="warn"
              class="warn cursor-pointer ml-[0.25rem]"
              @click="redirectToURL(order?.operator?.url)"
            />
          </div>
        </div>
        <div class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-4/12">Location</div>
          <div class="order-content-data w-8/12">
            <span class="cursor-pointer" @click="redirectToURL(order?.location?.url)">
              {{ order?.location?.full_repr }}</span
            >
            <img
              width="12"
              height="12"
              src="../../assets/icons/chevron-right.svg"
              alt="warn"
              class="warn cursor-pointer ml-[0.25rem]"
              @click="redirectToURL(order?.location?.url)"
            />
          </div>
        </div>
        <div
          v-if="order?.sfr && order?.tails.length > 1"
          class="order-content-el flex gap-3 items-start"
        >
          <div class="order-content-header w-4/12 cursor-pointer">S&F Request</div>
          <div class="order-content-data w-8/12 flex items-center gap-1">
            <div
              class="status px-[0.5rem] py-[0.25rem] border-0 rounded-md cursor-pointer"
              :style="{
                'background-color':
                  order?.sfr?.sfr_status?.background_color ?? 'rgb(255, 255, 255)',
                color: order?.sfr?.sfr_status?.text_color
              }"
              @click="redirectToURL(order?.sfr?.url)"
            >
              {{ order?.sfr?.reference }}
            </div>
          </div>
        </div>
      </div>
      <div class="order-content-col w-4/12 flex flex-col gap-1.5">
        <div
          v-if="!order?.fuel_order?.is_open_release"
          class="order-content-el flex gap-3 items-start"
        >
          <div class="order-content-header w-5/12">Uplift Time (Local)</div>
          <div class="order-content-data w-7/12">
            {{
              fuelUplifts && fuelUplifts.length > 0
                ? toLocalTime(fuelUplifts[0].time_z)
                : order?.fulfilment_datetime
                ? order.fulfilment_datetime_local_str
                : 'TBC'
            }}
          </div>
        </div>
        <div v-else class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-5/12">Release End Date</div>
          <div class="order-content-data w-7/12">
            {{
              order?.fuel_order?.departure_time_tbc
                ? order?.fuel_order?.departure_datetime_utc
                : order?.fuel_order?.deaprture_datetime_utc.slice(0, 10)
            }}
          </div>
        </div>
        <div class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-5/12">Fuel</div>
          <div v-if="!order?.fuel_order?.is_open_release" class="order-content-data w-7/12">
            {{
              `${order?.fuel_order?.fuel_category?.name}, ${addThousandSeparators(
                order?.fuel_order?.fuel_quantity
              )}
            ${order?.fuel_order?.fuel_uom?.description_plural}`
            }}
          </div>
          <div v-else class="order-content-data w-7/12 relative">
            {{ `${order?.fuel_order?.fuel_category?.name}` }}
            <div class="hover-wrap contents">
              <img
                width="16"
                height="16"
                src="../../assets/icons/info-circle.svg"
                alt="warn"
                class="warn"
              />
              <div class="order-content-data-tooltip">
                An indicative fuel quantity of
                {{ addThousandSeparators(order?.fuel_order?.fuel_quantity) }}
                {{ order?.fuel_order?.fuel_uom?.description_plural }} has been used for the purposes
                of calculating the order value and ROI
              </div>
            </div>
          </div>
        </div>
        <div class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-5/12">Supplier</div>
          <div class="order-content-data w-7/12">
            <span
              :class="{ 'cursor-pointer': order?.fuel_order?.supplier }"
              @click="redirectToURL(order?.fuel_order?.supplier?.url)"
              >{{ order?.fuel_order?.supplier?.details?.registered_name ?? 'TBC' }}</span
            >
            <img
              v-if="order?.fuel_order?.supplier"
              width="12"
              height="12"
              src="../../assets/icons/chevron-right.svg"
              alt="warn"
              class="warn cursor-pointer ml-[0.25rem]"
              @click="redirectToURL(order?.fuel_order?.supplier?.url)"
            />
          </div>
        </div>
        <div class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-5/12">Callsign</div>
          <div class="order-content-data w-7/12">
            {{ order?.callsign }}
          </div>
        </div>
      </div>
      <div class="order-content-col w-4/12 flex flex-col gap-1.5">
        <div class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-4/12">Handler</div>
          <div class="order-content-data w-8/12">
            <span
              :class="{ 'cursor-pointer': order?.fuel_order?.ground_handler }"
              @click="redirectToURL(order?.fuel_order?.ground_handler?.url)"
              >{{ order?.fuel_order?.ground_handler?.details?.registered_name ?? 'TBC' }}</span
            >
            <img
              v-if="order?.fuel_order?.ground_handler"
              width="12"
              height="12"
              src="../../assets/icons/chevron-right.svg"
              alt="warn"
              class="warn cursor-pointer ml-[0.25rem]"
              @click="redirectToURL(order?.fuel_order?.ground_handler?.url)"
            />
          </div>
        </div>
        <div class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-4/12">Aircraft</div>
          <div v-if="order?.is_any_aircraft" class="order-content-data w-8/12">Any aircraft</div>
          <div v-else-if="order?.tails.length > 0" class="order-content-data w-8/12 flex flex-col">
            <div v-for="aircraft in order?.tails" :key="aircraft.id">
              {{ aircraft?.tail_number?.full_repr ?? 'Aircraft' }}
            </div>
          </div>
          <div
            v-else-if="order?.tails.length === 0 && order?.aircraft_type"
            class="order-content-data w-8/12"
          >
            {{ order?.aircraft_type?.full_repr }}
          </div>
        </div>
        <div
          v-if="order?.sfr && order?.tails.length <= 1"
          class="order-content-el flex gap-3 items-start"
        >
          <div class="order-content-header w-4/12 cursor-pointer">S&F Request</div>
          <div class="order-content-data w-8/12 flex items-center gap-1">
            <div
              class="status px-[0.5rem] py-[0.25rem] border-0 rounded-md cursor-pointer"
              :style="{
                'background-color':
                  order?.sfr?.sfr_status?.background_color ?? 'rgb(255, 255, 255)',
                color: order?.sfr?.sfr_status?.text_color
              }"
              @click="redirectToURL(order?.sfr?.url)"
            >
              {{ order?.sfr?.reference }}
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="order?.type?.is_gh" class="order-content flex pb-[1rem] px-[1rem] gap-2">
      <div class="order-content-col w-5/12">
        <div class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-4/12">Callsign</div>
          <div class="order-content-data w-8/12">
            {{ order?.callsign }}
          </div>
        </div>
        <div class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-4/12">ETA (UTC)</div>
          <div class="order-content-data w-8/12">
            {{
              order?.gh_order?.arrival_time_tbc
                ? order?.gh_order?.arrival_datetime_utc + ' (Time TBC)'
                : order?.gh_order?.arrival_datetime_utc
            }}
          </div>
        </div>
        <div class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-4/12">ETA (Local)</div>
          <div class="order-content-data w-8/12">
            {{
              order?.gh_order?.arrival_time_tbc
                ? order?.gh_order?.arrival_datetime_utc + ' (Time TBC)'
                : toLocalTime(order?.gh_order?.arrival_datetime_utc!)
            }}
          </div>
        </div>
        <div class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-4/12">Location</div>
          <div class="order-content-data w-8/12">
            <span class="cursor-pointer" @click="redirectToURL(order?.location?.url)">
              {{ order?.location?.full_repr }}</span
            >
            <img
              width="12"
              height="12"
              src="../../assets/icons/chevron-right.svg"
              alt="warn"
              class="warn cursor-pointer ml-[0.25rem]"
              @click="redirectToURL(order?.location?.url)"
            />
          </div>
        </div>
        <div class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-4/12">Operator</div>
          <div class="order-content-data w-8/12">
            <span class="cursor-pointer" @click="redirectToURL(order?.operator?.url)">
              {{ order?.operator?.details?.registered_name }}</span
            >
            <img
              width="12"
              height="12"
              src="../../assets/icons/chevron-right.svg"
              alt="warn"
              class="warn cursor-pointer ml-[0.25rem]"
              @click="redirectToURL(order?.operator?.url)"
            />
          </div>
        </div>
      </div>
      <div class="order-content-col w-5/12">
        <div class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-4/12">Aircraft</div>
          <div v-if="order?.is_any_aircraft" class="order-content-data w-8/12">Any aircraft</div>
          <div v-else-if="order?.tails.length > 0" class="order-content-data w-8/12 flex flex-col">
            <div v-for="aircraft in order?.tails" :key="aircraft.id">
              {{ aircraft?.tail_number?.full_repr ?? 'Aircraft' }}
            </div>
          </div>
          <div
            v-else-if="order?.tails.length === 0 && order?.aircraft_type"
            class="order-content-data w-8/12"
          >
            {{ order?.aircraft_type?.full_repr }}
          </div>
        </div>
        <div class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-4/12">ETD (UTC)</div>
          <div class="order-content-data w-8/12">
            {{
              order?.gh_order?.departure_time_tbc
                ? order?.gh_order?.departure_datetime_utc + ' (Time TBC)'
                : order?.gh_order?.departure_datetime_utc
            }}
          </div>
        </div>
        <div class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-4/12">ETD (Local)</div>
          <div class="order-content-data w-8/12">
            {{
              order?.gh_order?.departure_time_tbc
                ? order?.gh_order?.departure_datetime_utc + ' (Time TBC)'
                : toLocalTime(order?.gh_order?.departure_datetime_utc!)
            }}
          </div>
        </div>
        <div class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-4/12">Supplier</div>
          <div class="order-content-data w-8/12">
            {{ order?.gh_order?.ground_handler?.details?.registered_name ?? 'TBC' }}
          </div>
        </div>
        <div v-if="order?.sfr" class="order-content-el flex gap-3 items-start">
          <div class="order-content-header w-4/12">S&F Request</div>
          <div
            class="order-content-data w-8/12 cursor-pointer"
            @click="redirectToURL(order?.sfr?.url)"
          >
            <div
              class="status px-[0.5rem] py-[0.25rem] border-0 rounded-md"
              :style="{
                'background-color':
                  order?.sfr?.sfr_status?.background_color ?? 'rgb(255, 255, 255)',
                color: order?.sfr?.sfr_status?.color
              }"
            >
              {{ order?.sfr?.reference }}
            </div>
          </div>
        </div>
      </div>
    </div>
    <ArrowProgress :steps="orderStatus?.progress"></ArrowProgress>
  </div>
</template>

<script lang="ts" setup>
import { computed, onBeforeMount, type PropType, ref, shallowRef, watch } from 'vue';
import { useQueryClient } from '@tanstack/vue-query';
import { useRoute, useRouter } from 'vue-router';
import { Button } from 'shared/components';
import { useOrderReferenceStore } from '@/stores/useOrderReferenceStore';
import { useOrderStore } from '@/stores/useOrderStore';
import { useQueryRefreshSupplierPricing, useQueryReinstateOrder } from '@/services/queries';
import {
  useQueryApproveOrder,
  useQueryGenerateSfFuelRelease,
  useQueryProceedCompliance
} from '@/services/queries';
import { useQueryFuelUplifts } from '@/services/queries/uplift';
import { redirectToURL } from '@/helpers';
import { changeColorAlpha } from '@/helpers/colors';
import { addThousandSeparators, toLocalTime, toUTCdateTime } from '@/helpers/order';
import { notify } from '@/helpers/toast';
import ArrowProgress from '../forms/ArrowProgress.vue';
import Avatar from '../forms/Avatar.vue';
import Loading from '../forms/Loading.vue';
import CancelOrderModal from '../modals/CancelOrderModal.vue';
import ConfirmGroundHandlingModal from '../modals/ConfirmGroundHandlingModal.vue';
import ConfirmSpfReconciliationModal from '../modals/ConfirmSpfReconciliationModal.vue';
import ConfirmSupplierOrderModal from '../modals/ConfirmSupplierOrderModal.vue';
import DeclineOrderModal from '../modals/DeclineOrderModal.vue';
import MarkNoUpliftModal from '../modals/MarkNoUpliftModal.vue';
import NoServicingTakenModal from '../modals/NoServicingTakenModal.vue';
import OldSystemDetailsModal from '../modals/OldSystemDetailsModal.vue';
import RequestGroundHandlingModal from '../modals/RequestGroundHandlingModal.vue';
import SendClientFuelReleaseModal from '../modals/SendClientFuelReleaseModal.vue';
import SendSupplierOrderRequestModal from '../modals/SendSupplierOrderRequestModal.vue';
import SendViaEmailModal from '../modals/SendViaEmailModal.vue';
import SubmitDeliveryTicketDetailsModal from '../modals/SubmitDeliveryTicketDetailsModal.vue';
import SupplierDeclinedOrderModal from '../modals/SupplierDeclinedOrderModal.vue';
import WaitingOnPricingModal from '../modals/WaitingOnPricingModal.vue';

import type { IFuelProgress, IGhProgress, IOrder, IOrderRefreshStatus } from 'shared/types';

type Modal =
  | 'decline'
  | 'send-email'
  | 'supplier-order-request'
  | 'supplier-order-request-update'
  | 'client-fuel-release'
  | 'mark-no-uplift'
  | 'confirm-supplier-order'
  | 'submit-delivery-ticket'
  | 'supplier-declined-order'
  | 'no-servicing-taken'
  | 'confirm-ground-handling'
  | 'request-ground-handling'
  | 'confirm-spf-reconciliation'
  | 'waiting-on-pricing'
  | 'details-old-system'
  | 'cancel-order';

const props = defineProps({
  order: {
    type: Object as PropType<IOrder | any>,
    default: () => null
  },
  orderStatus: {
    type: Object as PropType<IOrderRefreshStatus | null>,
    default: () => null
  }
});

const route = useRoute();
const router = useRouter();
const queryClient = useQueryClient();
const orderStore = useOrderStore();
const isFuel = computed(() => orderStore.order?.type?.is_fuel || false);
const isGh = computed(() => orderStore.order?.type?.is_gh || false);
const isQuote = computed(
  () =>
    props.orderStatus?.status?.status_details?.id === 'new_rfq' ||
    props.orderStatus?.status?.status_details?.id === 'in_progress_quote'
);
const isExpired = computed(() => props.orderStatus?.status?.status_details?.id === 'expired');
const orderId = computed(() => orderStore.orderId);
const currentStep = computed(() => orderStore.currentStep);
const supplierStatusId = computed(() => props.orderStatus?.supplier_status?.status_details?.id);

const orderReferenceStore = useOrderReferenceStore();
const orderPricing = computed(() => orderReferenceStore.orderPricing);
const isRefreshSupplierPricingButtonShown = computed(
  () =>
    isFuel.value &&
    orderStore.currentStep === 1 &&
    props.orderStatus?.status?.status_details?.id &&
    (!orderReferenceStore?.selectedSupplierInfo ||
      [
        'new_order',
        'order_reinstated',
        'amended',
        'supplier_pricing_missing',
        'supplier_pricing_expired'
      ].includes(props.orderStatus.status.status_details.id))
);

const modal = shallowRef<Modal | null>(null);

const isComplianceStep = computed(() =>
  Boolean(orderStore.currentStep === 2 && orderStore.order?.type?.is_fuel)
);

const header = ref<HTMLElement | null>(null);

const { refetch: approveOrder, isFetching: isFetchingApproveOrder } = useQueryApproveOrder(
  orderId,
  {
    enabled: false
  }
);
const { data: proceedComplianceData } = useQueryProceedCompliance(orderId, {
  enabled: isComplianceStep,
  retry: false
});

const { data: fuelUplifts } = useQueryFuelUplifts(orderId, {
  retry: false,
  enabled: isFuel
});

const { refetch: reinstateOrder, isFetching: isFetchingReinstateOrder } = useQueryReinstateOrder(
  orderId,
  {
    enabled: false,
    retry: false
  }
);

const { refetch: generateSfFuelRelease, isFetching: isFetchingGenerateSfFuelRelease } =
  useQueryGenerateSfFuelRelease(orderId, {
    enabled: false,
    retry: false
  });

const { refetch: refreshSupplierPricing, isFetching: isFetchingRefreshSupplierPricing } =
  useQueryRefreshSupplierPricing(orderId, {
    enabled: false,
    retry: false
  });

const isLoadingFuelStepOne = computed(
  () => orderReferenceStore?.isLoadingSupplyFuel || isFetchingRefreshSupplierPricing.value
);
const isFetchingOrder = computed(() => orderStore.isFetchingOrder);
const isStatus = computed(() => props.orderStatus || orderStore.order?.status);
const isDeclined = computed(
  () => props.orderStatus?.status?.status_details?.id === 'declined_by_management'
);
const isLoading = computed(
  () =>
    isLoadingFuelStepOne.value ||
    isFetchingApproveOrder.value ||
    isFetchingGenerateSfFuelRelease.value ||
    isFetchingReinstateOrder.value ||
    isFetchingOrder.value
);

function getColor() {
  return props.orderStatus?.status?.status_details?.fill_colour_hex ?? '#fff';
}

function getTextColor() {
  let hex = props.orderStatus?.status?.status_details?.fill_colour_hex ?? '#000000';
  const amount = 80;
  hex = hex.replace(/^#/, '');
  let r = parseInt(hex.substring(0, 2), 16);
  let g = parseInt(hex.substring(2, 4), 16);
  let b = parseInt(hex.substring(4, 6), 16);
  r = Math.max(0, r - amount);
  g = Math.max(0, g - amount);
  b = Math.max(0, b - amount);
  const darkenedColor = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b
    .toString(16)
    .padStart(2, '0')}`;
  return darkenedColor;
}

type CloseModalOptions = {
  disableRouteChange?: boolean;
};

const closeModal = (options?: CloseModalOptions) => {
  modal.value = null;
  if (!options?.disableRouteChange) router.push({ query: { ...route.query, modal: undefined } });
};

const redirectToLinkedOrder = (uri: string) => {
  console.log(uri);
};

const onProceedToCompliance = async () => {
  orderStore.changeStep(2);
  if (isFuel.value) {
    await queryClient.invalidateQueries({ queryKey: ['proceedCompliance', orderId.value] });
  }
  queryClient.invalidateQueries({ queryKey: ['orderStatus', orderId.value] });
};

const openModal = (modalName: Modal) => {
  modal.value = modalName;
  router.push({ query: { ...route.query, modal: modalName } });
};

const onApproveOrder = async () => {
  try {
    await approveOrder();
    queryClient.invalidateQueries({ queryKey: ['orderStatus', orderId.value] });
    queryClient.invalidateQueries({ queryKey: ['proceedCompliance', orderId.value] });
    orderStore.changeStep(3);
  } catch (error) {
    console.error(error);
  }
};

const onIssueFuelRelease = async () => {
  try {
    const response = await generateSfFuelRelease();

    if ('details' in response && typeof response.details === 'string') {
      notify(response.details, 'success');
    }

    if ('errors' in response && Array.isArray(response.errors)) {
      notify(response.errors[0], 'error');
    }

    queryClient.invalidateQueries({ queryKey: ['orderStatus', orderId.value] });
  } catch (error) {
    console.error(error);
  }
};

const onRefreshSupplierPricing = async () => {
  const response = await refreshSupplierPricing();
  await orderStore.fetchOrder(orderId.value);
  await orderReferenceStore?.fetchSupplierFuel(response.data?.new_pricing_results_record_id);
  queryClient.invalidateQueries({ queryKey: ['activityLog', orderId.value] });
};

const onReinstateOrder = async () => {
  await reinstateOrder();
  queryClient.invalidateQueries({ queryKey: ['orderStatus', orderId.value] });
  orderStore.changeStep(1);
  await orderStore.fetchOrder(orderId.value);
  await orderReferenceStore?.initiateReferenceStore(
    orderId.value,
    orderStore?.order?.pricing_calculation_record
  );
};

onBeforeMount(() => {
  const searchParams = new URLSearchParams(window.location.search);
  const queryModal = searchParams.get('modal');

  switch (queryModal) {
    case 'supplier-order-request':
      modal.value = queryModal;
      orderStore.changeStep(3);
      break;
  }
});

watch(
  () => orderStore.isClientQuoteSent,
  (value) => {
    if (value) {
      queryClient.invalidateQueries({ queryKey: ['orderStatus', orderId.value] });
      orderStore.sendClientQuote(false);
    }
  }
);

defineExpose({
  header
});
</script>

<style lang="scss">
.order-header {
  .button {
    background-color: theme('colors.base.0') !important;
    color: theme('colors.blue.500') !important;
    border: 1px solid theme('colors.base.300') !important;
    @apply flex shrink-0 focus:shadow-none mb-0 mt-0 p-[0.5rem] px-[1rem] rounded-lg #{!important};

    &:hover {
      background-color: rgb(224, 228, 249) !important;
    }

    &-green {
      background-color: rgba(11, 161, 125, 1) !important;
      color: rgba(255, 255, 255, 1) !important;

      &:hover {
        background-color: rgb(13, 196, 152) !important;
      }

      img {
        filter: brightness(0) saturate(100%) invert(100%) sepia(100%) saturate(0%)
          hue-rotate(251deg) brightness(102%) contrast(103%);
      }
    }

    &-yellow {
      color: rgba(111, 73, 17, 1) !important;
      border-color: rgba(254, 161, 22, 1) !important;
      &:hover {
        background-color: #fcf7ee !important;
      }
    }

    &-expired {
      background-color: #f3c78e !important;
      color: #8b550f !important;
      &:hover {
        background-color: #f7d8b0 !important;
      }

      img {
        filter: brightness(0) saturate(100%) invert(34%) sepia(17%) saturate(2448%)
          hue-rotate(357deg) brightness(96%) contrast(90%);
      }
    }

    &:disabled {
      background-color: rgb(241, 242, 246) !important;
      color: rgb(139, 148, 178) !important;
    }
  }

  .cancel-button {
    background-color: theme('colors.base.0') !important;
    color: theme('colors.system.red') !important;
    border: 1px solid theme('colors.system.red') !important;

    img {
      filter: brightness(0) saturate(100%) invert(71%) sepia(81%) saturate(4491%) hue-rotate(321deg)
        brightness(100%) contrast(108%);
    }

    &:hover {
      background-color: rgb(255, 216, 216) !important;
    }
  }

  .send-via-email-popup {
    .el {
      color: theme('colors.main');
      font-size: 16px;
      font-weight: 500;

      &-red {
        color: rgba(254, 98, 98, 1);
      }
    }
  }

  .status {
    font-size: 12px;
    height: 42px;
    max-height: 42px;
    display: flex;
    align-items: center;
  }

  .order-status {
    .status {
      font-size: 16px;
      font-weight: 600;
    }
  }

  .order-name {
    font-size: 22px;
    font-weight: bold;
  }

  .order-linked {
    border: 1px solid rgba(223, 226, 236, 1);
    border-radius: 6px;

    &-text {
      font-size: 12px;
      font-weight: 500;
      color: rgba(82, 90, 122, 1);
    }

    img {
      width: 12px !important;
      height: 12px !important;
    }
  }

  .order-company {
    color: rgba(60, 67, 93, 1);
    font-size: 15px;
    font-weight: 400;
  }

  .order-content-header {
    font-size: 14px;
    color: rgba(82, 90, 122, 1);
  }

  .order-content-data {
    font-size: 16px;
    color: theme('colors.main');
    font-weight: 500;

    &-tooltip {
      display: none;
      position: absolute;
      background-color: rgb(81, 93, 138);
      color: rgb(255, 255, 255);
      font-size: 12px;
      font-weight: 400;
      z-index: 10;
      padding: 0.5rem;
      border-radius: 0.5rem;
      bottom: 2rem;
      right: 0;
      min-width: 30vw;

      &::before {
        content: '';
        position: absolute;
        width: 10px;
        height: 10px;
        background-color: rgb(81, 93, 138);
        transform: rotate(45deg);
        right: 4rem;
        bottom: -5px;
      }
    }
  }

  .hover-wrap {
    &:hover {
      .order-content-data-tooltip {
        display: block;
      }
    }
  }
}
</style>
