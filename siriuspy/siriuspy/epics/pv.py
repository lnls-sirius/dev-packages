import epics as _epics


class PV(_epics.pv.PV):

    # @_epics.pv._ensure_context
    def set_auto_monitor(self, mask=True):
        if not self.connected:
            return
        elif not mask:
            self.clear_auto_monitor()
            return
        elif self._monref is not None:
            return

        self.auto_monitor = mask
        maxcount = 0
        if self._args['count'] is not None:
            maxcount = self._args['count']
        # you can explicitly request a subscription mask
        # (ie dbr.DBE_ALARM|dbr.DBE_LOG) by passing it as the
        # auto_monitor arg, otherwise if you specify 'True' you'll
        # just get the default set in ca.DEFAULT_SUBSCRIPTION_MASK
        if self.auto_monitor is True:
            mask = _epics.ca.DEFAULT_SUBSCRIPTION_MASK
        else:
            mask = self.auto_monitor
        use_ctrl = self.form == 'ctrl'
        self._monref = _epics.ca.create_subscription(
            self.chid, use_ctrl=use_ctrl, use_time=not use_ctrl,
            callback=self.__on_changes, mask=mask, count=maxcount)
