# Filter Basket

![Filter Basket logo](filter_basket.svg)

Filter a target vector layer using values picked from a source vector layer.

Version 1.4.1 | QGIS 3.x and 4.x | License: GPL v3

A detailed [User Guide (PDF)](Filter_Basket_User_Guide.pdf) with worked examples is included in this folder.

## Features

- Pick values directly from features on the map canvas
- Drag a rectangle to select multiple features and groups at once
- Group related source features with a **Group Field**
- Display selected values under headers such as `Group (site_id): SITE-01`
- Remove a whole group from its list header
- Resolve overlapping features with the **Select Source Value** dialog
- Temporarily preview filtered Selected Target values with **Include/Exclude**
- Highlight picked source geometries on the canvas
- Type-aware filters for string, numeric, and boolean target fields
- Filter re-applies when the target layer or field changes
- Layer and field choices saved between sessions

## Installation

1. Copy this folder into the Python plugins folder of your active QGIS profile.
   - Windows: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins`
2. Restart QGIS.
3. Open **Plugins > Manage and Install Plugins > Installed** and enable **Filter Basket**.
4. A toolbar button and a Plugins menu entry appear.



## Quick start

1. Choose the **Source Layer** and the **Target Layer**.
2. Choose the **Group Field**, **Source Field**, and **Target Field**.
3. Click **Activate Pick Tool**.
4. Click a feature on the map, or drag a rectangle to select multiple features. Tick the values you want and click **Add Selected**.
5. The values appear under a `Group (field_name): value` header, the target layer is filtered, and the picked features are highlighted.
6. Optionally use **Include/Exclude** and **Preview Filter** to temporarily narrow the Selected Target list; click **Restore Full List** to return.
7. Click **Clear All** to see the full target layer again.

## Interface

| Control | Purpose |
| --- | --- |
| Source Layer | Vector layer to pick features from |
| Target Layer | Vector layer that will be filtered |
| Group Field | Source field whose value groups features together |
| Source Field | Field on the source layer holding the values to collect |
| Target Field | Field on the target layer to filter against |
| Activate Pick Tool | Turn map click/rectangle drag into a value picker |
| Reload Layers | Refresh layer lists after adding layers in QGIS |
| Help | Show a short description of the workflow |
| Selected Target | Values used in the filter, grouped under Group Field headers |
| Include / Exclude | Comma-separated substrings to temporarily keep or remove values in Selected Target |
| Preview Filter | Apply the temporary Include/Exclude filter to Selected Target |
| Restore Full List | Restore Selected Target to the state before Preview Filter |
| Clear All | Clear values, remove the filter, and delete highlights |


### Grouped Selected Target list

Selected values are displayed under bold, non-selectable headers in the form `Group (field_name): group_value`, for example `Group (site_id): SITE-01`. The field name is captured when the group is picked, so headers stay correct even if the Group Field combo changes later.

| Action | Result |
| --- | --- |
| Right-click a value | Remove it from every group and update the filter |
| Press Delete on a value | Same as Remove |
| Right-click a group header | **Remove group** — remove the whole group and its highlights |

If the same value belongs to more than one group it appears under each group. Removing the value removes it everywhere. Removing a group keeps a shared value in the filter as long as another group still contains it.

### Rectangle selection (beta)

With **Activate Pick Tool** active, drag a rectangle on the map to select multiple source features. A **Select Source Values** dialog shows all values inside the rectangle, grouped by the Group Field, with all hits checked by default. Tick or untick values as needed, then click **Add Selected**. This works across one or multiple groups.

### Temporary preview filter

Use **Include** or **Exclude** to temporarily narrow the Selected Target list without losing the original selection. Enter comma-separated substrings, for example `G18` or `G18,G21`, then click **Preview Filter**. Matching is case-insensitive and applies to Selected Target values.

- **Include** keeps only values containing any listed substring.
- **Exclude** removes values containing any listed substring.
- Typing in one box clears the other.
- **Restore Full List** restores the original selection, filter, and highlights.
- While Preview Filter is active, new map selections are added to the full list and automatically filtered by the active Include/Exclude; removals apply to the full list. Click **Restore Full List** to see all values.

## Examples

### Basic pick

Source layer `Sites` has `site_id` and `sector_id`; target layer `Measurements` has `sector_id`.

| Setting | Value |
| --- | --- |
| Source Layer | Sites |
| Group Field | site_id |
| Source Field | sector_id |
| Target Layer | Measurements |
| Target Field | sector_id |

Click a `SITE-01` feature, tick `SITE-01-A` and `SITE-01-B`, then click **Add Selected**. The list shows a `Group (site_id): SITE-01` header above both values, and the target layer is filtered with:

```sql
"sector_id" IN ('SITE-01-A','SITE-01-B')
```

### Remove a whole group

- **Right-click a group header** and choose **Remove group** to remove the whole group and its highlights. A shared value stays in the filter if another group still contains it.

### Overlapping features

When several source features lie under the cursor, **Select Source Value** lists each feature's Source Field value. Choose one row and click **OK** to use that feature's group.

### Remove a single value

Right-click a value in **Selected Target** and choose **Remove**, or select it and press **Delete**. The value is removed from every group it appears in, and empty group headers disappear automatically.

### Temporary preview filter example

With a Selected Target list containing values from two groups:

```text
group1: BD4G18_4510324E_4, BD4G18_4510324E_5, BD4G18_4510324E_6, BD4G21_4510324E21_7, ...
group2: BD4G18_4518333E_4, BD4G18_4518333E_5, BD4G18_4518333E_6, BD4G21_4518333E21_7, ...
```

Enter `G18` in **Include** and click **Preview Filter**. Only G18 values remain, grouped as before. Click **Restore Full List** to return the original selection.

### Numeric target fields

Values are written unquoted for numeric fields:

```sql
"sector_no" IN (101,102)
```

Boolean fields use `TRUE` / `FALSE`. Strings are quoted and apostrophes escaped (`O'Brien` becomes `'O''Brien'`).

### General example - Zones and Events (non-telecom)

This example uses completely generic layers and shows that Filter Basket is not tied to telecom or site/cell data. The goal is to show only events located in selected zones.

| Setting | Value |
| --- | --- |
| Source Layer | Zones (polygon) |
| Group Field | district |
| Source Field | zone_code |
| Target Layer | Events (point) |
| Target Field | zone_code |

The Zones layer contains district `North` with codes `N-01` and `N-02`, and district `South` with `S-01` and `S-02`.

1. Click **Activate Pick Tool**, then click a zone in district `North`.
2. The dialog titled **Group: North** lists `N-01` and `N-02`.
3. Tick both values and click **Add Selected**.
4. Only events whose `zone_code` is `N-01` or `N-02` are drawn.

```sql
"zone_code" IN ('N-01','N-02')
```

The list shows a `Group (district): North` header above `N-01` and `N-02`. Right-clicking the header removes that group. The same pattern works for any grouped data: regions and customers, departments and staff, parcels and permits, batches and orders.

### General example - Numeric keys

Numeric target fields need no quotes. Here a `Batches` layer supplies batch numbers used to filter an `Orders` layer.

| Setting | Value |
| --- | --- |
| Source Layer | Batches |
| Group Field | supplier |
| Source Field | batch_no |
| Target Layer | Orders |
| Target Field | batch_no (integer) |

Pick batches `101` and `102` for supplier A, then click **Add Selected**:

```sql
"batch_no" IN (101,102)
```

### Reload layers

After adding a layer in QGIS, click **Reload Layers**. Only vector layers are listed, and current layer and field selections are restored where possible.

## How filtering works

- Values are stored per group and the filter uses the union of all groups, so duplicates are ignored.
- The Selected Target list shows a bold header per group, labelled with the Group Field name captured at pick time.
- Removing a value removes it from all groups; removing a group keeps shared values that other groups still contain.
- A subset expression is built on the selected Target Field using `setSubsetString()`.
- Field names are double-quoted and escaped; string values are single-quoted and escaped.
- Changing the Target Layer or Target Field re-applies the filter.
- **Clear All** sets an empty subset string, showing every feature again.

## Saved settings

Layer and field choices are stored in `QgsSettings` and restored on next load:

```
MRFilter/source_layer
MRFilter/mr_layer
MRFilter/tower_field
MRFilter/source_cell_field
MRFilter/mr_cell_field
```

Selected values and highlights are not saved between sessions.

## Compatibility

- QGIS 3.x and 4.x; `qgisMaximumVersion=4.99`
- `qgis.PyQt` compatibility imports and scoped Qt enums work with Qt5 and Qt6
- `QAction` is imported from `qgis.PyQt.QtGui` as required by Qt6

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| A layer is missing from the combos | Only vector layers are listed; click Reload Layers |
| No values appear after a click | Confirm the Group Field and Source Field names |
| The filter hides everything | Check the Target Field type and that values match exactly |
| The toolbar icon does not appear | Reload the plugin or restart QGIS |
| Old highlights remain | Click Clear All |
| A value disappeared from other groups too | Value removal is global by design; remove the whole group instead if needed |

## Limitations

- One target layer is filtered at a time
- Selected values and highlights are not persisted between sessions
- Reload restores settings by layer name, so renamed layers may not be restored
- The group field name in a header is captured when that group is picked
- The target layer provider must support subset strings

## License

See [LICENSE](LICENSE) (GNU General Public License v3).
