## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">Customers</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field label="Customer Source">
      <b-select name="sideshow.orders.use_local_customers"
                  v-model="simpleSettings['sideshow.orders.use_local_customers']"
                  @input="settingsNeedSaved = true">
        <option value="true">Local Customers (in Sideshow)</option>
        <option value="false">External Customers (e.g. in POS)</option>
      </b-select>
    </b-field>
  </div>

  <h3 class="block is-size-3">Products</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field>
      <b-checkbox name="sideshow.orders.allow_item_discounts"
                  v-model="simpleSettings['sideshow.orders.allow_item_discounts']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow per-item discounts
      </b-checkbox>
    </b-field>

    <b-field v-show="simpleSettings['sideshow.orders.allow_item_discounts']">
      <b-checkbox name="sideshow.orders.allow_item_discounts_if_on_sale"
                  v-model="simpleSettings['sideshow.orders.allow_item_discounts_if_on_sale']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow discount even if item is on sale
      </b-checkbox>
    </b-field>

    <div v-show="simpleSettings['sideshow.orders.allow_item_discounts']"
         class="level-left block">
      <div class="level-item">Default item discount</div>
      <div class="level-item">
        <b-input name="sideshow.orders.default_item_discount"
                 v-model="simpleSettings['sideshow.orders.default_item_discount']"
                 @input="settingsNeedSaved = true"
                 style="width: 5rem;" />
      </div>
      <div class="level-item">%</div>
    </div>

    <b-field label="Product Source">
      <b-select name="sideshow.orders.use_local_products"
                  v-model="simpleSettings['sideshow.orders.use_local_products']"
                  @input="settingsNeedSaved = true">
        <option value="true">Local Products (in Sideshow)</option>
        <option value="false">External Products (e.g. in POS)</option>
      </b-select>
    </b-field>

    <b-field label="New/Unknown Products"
             message="If set, user can enter details of an arbitrary new &quot;pending&quot; product.">
      <b-checkbox name="sideshow.orders.allow_unknown_products"
                  v-model="simpleSettings['sideshow.orders.allow_unknown_products']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow creating orders for new/unknown products
      </b-checkbox>
    </b-field>

    <div v-show="simpleSettings['sideshow.orders.allow_unknown_products']"
         style="padding-left: 2rem;">

      <p class="block">
        Require these fields for new product:
      </p>

      <div class="block"
           style="margin-left: 2rem;">
        % for field in pending_product_fields:
            <b-field>
              <b-checkbox name="sideshow.orders.unknown_product.fields.${field}.required"
                          v-model="simpleSettings['sideshow.orders.unknown_product.fields.${field}.required']"
                          native-value="true"
                          @input="settingsNeedSaved = true">
                ${field}
              </b-checkbox>
            </b-field>
        % endfor
      </div>

    </div>
  </div>

  <h3 class="block is-size-3">Batches</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field label="New Order Batch Handler">
      <input type="hidden"
             name="wutta.batch.neworder.handler.spec"
             :value="simpleSettings['wutta.batch.neworder.handler.spec']" />
      <b-select v-model="simpleSettings['wutta.batch.neworder.handler.spec']"
                @input="settingsNeedSaved = true">
        <option :value="null">(use default)</option>
        <option v-for="handler in batchHandlers"
                :key="handler.spec"
                :value="handler.spec">
          {{ handler.spec }}
        </option>
      </b-select>
    </b-field>
  </div>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.batchHandlers = ${json.dumps(batch_handlers)|n}

  </script>
</%def>
