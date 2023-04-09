from packaging import version
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from pandas.plotting._matplotlib.hist import (HistPlot as _HistPlot,
                                              KdePlot as _KdePlot)
import pandas.plotting._matplotlib.hist
from pandas.core.dtypes.missing import (
    isna,
    remove_na_arraylike,
)
from pandas.io.formats.printing import pprint_thing
from pandas.plotting._matplotlib.core import MPLPlot
from pandas.plotting._matplotlib.groupby import (create_iter_data_given_by,
                                                 reformat_hist_y_given_by)
from typing import Literal
from wpandas.plotting._matplotlib.core import (
    _WeightedMPLPlot, _CompressedMPLPlot, _get_weights
)


class HistPlot(_WeightedMPLPlot, _HistPlot):
    # noqa: disable=D101
    def _calculate_bins(self, data):
        nd_values = data.infer_objects(copy=False)._get_numeric_data()
        values = np.ravel(nd_values)
        weights = self.kwds.get("weights", None)
        if weights is not None:
            try:
                weights = np.broadcast_to(weights[:, None], nd_values.shape)
            except ValueError:
                print(nd_values.shape, weights.shape)
                pass
            weights = np.ravel(weights)
            weights = weights[~isna(values)]

        values = values[~isna(values)]

        hist, bins = np.histogram(
            values, bins=self.bins, range=self.kwds.get("range", None),
            weights=weights
        )
        return bins

    def _get_colors(self, num_colors=None, color_kwds='color'):
        if (self.colormap is not None and self.kwds.get(color_kwds) is None
           and (num_colors is None or num_colors == 1)):
            return [plt.get_cmap(self.colormap)(0.68)]
        return super()._get_colors(num_colors, color_kwds)

    def _make_plot(self):  # pragma: no cover
        # TODO: remove when these changes have been added to pandas
        if version.parse(pd.__version__) >= version.parse("2.0.0"):
            return super()._make_plot()

        colors = self._get_colors()
        stacking_id = self._get_stacking_id()

        # Re-create iterated data if `by` is assigned by users
        data = (
            create_iter_data_given_by(self.data, self._kind)
            if self.by is not None
            else self.data
        )

        for i, (label, y) in enumerate(self._iter_data(data=data)):
            ax = self._get_ax(i)

            kwds = self.kwds.copy()

            label = pprint_thing(label)
            label = self._mark_right_label(label, index=i)
            kwds["label"] = label

            style, kwds = self._apply_style_colors(colors, kwds, i, label)
            if style is not None:
                kwds["style"] = style

            kwds = self._make_plot_keywords(kwds, y)

            # the bins is multi-dimension array now and each plot need only 1-d
            # and when by is applied, label should be columns that are grouped
            if self.by is not None:
                kwds["bins"] = kwds["bins"][i]
                kwds["label"] = self.columns
                kwds.pop("color")

            # We allow weights to be a multi-dimensional array, e.g. a (10, 2)
            # array, and each sub-array (10,) will be called in each iteration.
            # If users only provide 1D array, we assume the same weights are
            # used for all columns
            weights = kwds.get("weights", None)
            if weights is not None:
                if np.ndim(weights) != 1 and np.shape(weights)[-1] != 1:
                    try:
                        weights = weights[:, i]
                    except IndexError as err:
                        raise ValueError(
                            "weights must have the same shape as data, "
                            "or be a single column"
                        ) from err
                weights = weights[~isna(y)]
                kwds["weights"] = weights

            y = reformat_hist_y_given_by(y, self.by)

            artists = self._plot(ax, y, column_num=i,
                                 stacking_id=stacking_id, **kwds)

            # when by is applied, show title for subplots to
            # know which group it is
            if self.by is not None:
                ax.set_title(pprint_thing(label))

            self._append_legend_handles_labels(artists[0], label)

    def _post_plot_logic(self, ax, data):
        super()._post_plot_logic(ax, data)
        ax.set_yticks([])
        ax.set_ylim(bottom=0)
        ax.set_xlim(self.bins[0], self.bins[-1])


class KdePlot(HistPlot, _KdePlot):
    # noqa: disable=D101
    @classmethod
    def _plot(
        cls,
        ax,
        y,
        style=None,
        bw_method=None,
        ind=None,
        column_num=None,
        stacking_id=None,
        **kwds,
    ):
        from scipy.stats import gaussian_kde
        weights = kwds.pop("weights", None)

        y = remove_na_arraylike(y)
        gkde = gaussian_kde(y, bw_method=bw_method, weights=weights)

        y = gkde.evaluate(ind)
        lines = MPLPlot._plot(ax, ind, y, style=style, **kwds)
        return lines

    def _post_plot_logic(self, ax, data):
        ax.set_yticks([])
        ax.set_ylim(bottom=0)


def hist_frame(data, *args, **kwds):
    # noqa: disable=D103
    _get_weights(kwds, data)
    return pandas.plotting._matplotlib.hist_frame(data, *args, **kwds)


def hist_series(data, *args, **kwds):
    # noqa: disable=D103
    _get_weights(kwds, data)
    return pandas.plotting._matplotlib.hist_series(data, *args, **kwds)