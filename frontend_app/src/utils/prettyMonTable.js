
// function to format fields for rendering monitoring table. VUE V-for easier works with arrays instead of dictionaries
export function formatHeaderOutput(headerData) {
    let formattedData = {} // new header data formatted to fill the table
    let clusteredFields = [] // contains name of big field (cpu, mem ...)
    let clusteredFieldsSpan = [] // contains column span size for big field (cpu, mem ...)
    let fields = [] // all table fields
    let fieldsDataType = [] // datatypes of all table fields

    let keys = Object.keys(headerData);
    keys.shift()

    for (var key of keys){
        clusteredFields.push(key)
        clusteredFieldsSpan.push(Object.keys(headerData[key]).length)

        fields = fields.concat(Object.keys(headerData[key]))
        fieldsDataType = fieldsDataType.concat(Object.values(headerData[key]))
    }
    formattedData['clustered_fields'] = clusteredFields
    formattedData['clustered_fields_span'] = clusteredFieldsSpan
    formattedData['fields'] = fields
    formattedData['fields_data_type'] = fieldsDataType
    return formattedData
}

// function to format compute nodes data to render in v-for with data of formatted header
export function formatComputeNodeOutput(computeNodesData) {
    let formattedData = {}
    let keys = Object.keys(computeNodesData);
    for (var key of keys){
        formattedData = Object.assign({}, formattedData, computeNodesData[key])
    }
    let node_name = computeNodesData.header.split('!')['2']
    formattedData['name'] = node_name
    return formattedData
}