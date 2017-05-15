#!/usr/bin/python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
import xlwt

workbook = xlwt.Workbook()
tree = ET.ElementTree(file='file.xml')
eventTree = ET.ElementTree(file='Eventlog.txt')
patientVisitEvents = eventTree.getroot()
normalizedNameCounters = {}  ## {"单硝酸异山梨酯":3}
starttimeCounter = {}  ## {"1",1}
interventionCounter = {}
patientIdDic = {}  ## {"830564_2":2008}
logyearInterventionNum = {}  ## {"2008":{"单硝酸异山梨酯":3}}
allCount = 0
for patientTrace in patientVisitEvents:
    interventionCount = 0
    patientId = patientTrace.attrib['PatientId']
    admissionTime = patientTrace.attrib['AdmissionTime'][0:4] + str(
        (int(patientTrace.attrib['AdmissionTime'][5:7]) - 1) / 3)
    print admissionTime
    patientIdDic[patientId] = admissionTime
    if admissionTime not in logyearInterventionNum:
        logyearInterventionNum[admissionTime] = {}
    for record in patientTrace:
        if (record.tag == "Intervention"):
            allCount += 1
            normalizedName = record.attrib['NormalizedName']
            if normalizedName in normalizedNameCounters:
                normalizedNameCounters[normalizedName] += 1
            else:
                normalizedNameCounters[normalizedName] = 1
            if normalizedName in logyearInterventionNum[admissionTime]:
                logyearInterventionNum[admissionTime][normalizedName] += 1
            else:
                logyearInterventionNum[admissionTime][normalizedName] = 1
            happenDay = int(record.attrib['HappenDay'])
            if happenDay in starttimeCounter:
                starttimeCounter[happenDay] += 1
            else:
                starttimeCounter[happenDay] = 1
            interventionCount += 1
    if patientId in interventionCounter:
        interventionCounter[patientId] += interventionCount
    else:
        interventionCounter[patientId] = interventionCount

normalizedNameDict = sorted(normalizedNameCounters.iteritems(), key=lambda d: d[1], reverse=True)
for i in range(50):
    print normalizedNameDict[i][0], normalizedNameDict[i][1], format(normalizedNameDict[i][1] * 1.0 / allCount, '0.4%')
sheet = workbook.add_sheet("intervention list")
for i in range(len(normalizedNameDict)):
    sheet.write(i, 0, normalizedNameDict[i][0])
    sheet.write(i, 1, normalizedNameDict[i][1])
    sheet.write(i, 2, format(normalizedNameDict[i][1] * 1.0 / allCount, '0.4%'))

sheet = workbook.add_sheet("happen day")
starttimeDict = sorted(starttimeCounter.iteritems(), key=lambda d: d[0], reverse=False)
for i in range(len(starttimeDict)):
    print "happen day", starttimeDict[i][0], starttimeDict[i][1]
    sheet.write(i, 0, starttimeDict[i][0])
    sheet.write(i, 1, starttimeDict[i][1])

print "max Intervention", max(interventionCounter.values())
print "min Intervention", min(interventionCounter.values())
print "sum Intervention", sum(interventionCounter.values())
print "ave Intervention", sum(interventionCounter.values()) / len(interventionCounter.values())

anomalylistTree = ET.ElementTree(file='/Users/cm/Downloads/AnomalyList vLow=0.001.xml')
anomalyEventList = anomalylistTree.getroot()
allDays = 0
count = 0
longest = 0
shortest = 100
anomalyCounter = {}  ## {"830564_2":{"LESS":{"单硝酸异山梨酯":3}}}
anomalyTimes = 0
for anomalyInSingleTrace in anomalyEventList:
    days = int(anomalyInSingleTrace.attrib['LOS'])
    patientId = anomalyInSingleTrace.attrib['PatientAndVisitID']
    if patientId not in anomalyCounter:
        anomalyCounter[patientId] = {}
    if days > longest:
        longest = days
    if days < shortest:
        shortest = days
    allDays += days
    count += 1
    for anomaly in anomalyInSingleTrace:
        if anomaly.tag == 'Anomaly':
            anomalyType = anomaly.get('AnomalyType', 'no AnomalyType')
            interventionName = anomaly.get('InterventionName')
            if anomalyType == 'no AnomalyType':
                print anomaly.attrib['MACEType']
            if anomalyType in anomalyCounter[patientId]:
                if interventionName in anomalyCounter[patientId][anomalyType]:
                    anomalyCounter[patientId][anomalyType][interventionName] += 1
                else:
                    anomalyCounter[patientId][anomalyType][interventionName] = 1
            else:
                anomalyCounter[patientId][anomalyType] = {}
                anomalyCounter[patientId][anomalyType][interventionName] = 1
            anomalyTimes += 1

print "alldays : ", allDays
print "count : ", count
print "averange : ", allDays / count
print "longest : ", longest
print "shortest : ", shortest
# print anomalyCounter['B683648_1']

allSixCounter = {}  ## {"单硝酸异山梨酯":3}
eachSixDic = {}  ##  {"LESS":{"单硝酸异山梨酯":3}}

## {"830564_2":{"LESS":{"单硝酸异山梨酯":3}}}
for idAnomalyType in anomalyCounter.iteritems():
    for anomalyType in idAnomalyType[1].iteritems():
        if anomalyType[0] not in eachSixDic:
            eachSixDic[anomalyType[0]] = {}
        for i in anomalyType[1].iteritems():
            if i[0] in allSixCounter:
                allSixCounter[i[0]] += i[1]
            else:
                allSixCounter[i[0]] = i[1]
            if i[0] in eachSixDic[anomalyType[0]]:
                eachSixDic[anomalyType[0]][i[0]] += i[1]
            else:
                eachSixDic[anomalyType[0]][i[0]] = i[1]

                # print anomalyType[0], i[0], i[1], format(i[1] * 1.0 / normalizedNameCounters.get(i[0], -1), '0.4%')

sheet = workbook.add_sheet("rate")
index = 0
for i in eachSixDic.iteritems():
    for j in i[1].iteritems():
        print i[0], j[0], j[1], format(j[1] * 1.0 / normalizedNameCounters.get(j[0], -1), '0.4%'), format(
            j[1] * 1.0 / allSixCounter.get(j[0], -1), '0.4%')
        sheet.write(index, 0, i[0])
        sheet.write(index, 1, j[0])
        sheet.write(index, 2, j[1])
        sheet.write(index, 3, format(j[1] * 1.0 / normalizedNameCounters.get(j[0], -1), '0.4%'))
        sheet.write(index, 4, format(j[1] * 1.0 / allSixCounter.get(j[0], -1), '0.4%'))
        index += 1
## {"830564_2":{"LESS":{"单硝酸异山梨酯":3}}}
yearInterventionNum = {}  ## {"2008":{"单硝酸异山梨酯":3}}
yearAnomalyInterventionDict = {}  ##{"2008":{"LESS":{"单硝酸异山梨酯":3}}}

for idAnomalyType in anomalyCounter.iteritems():
    for anomalyType in idAnomalyType[1].iteritems():
        for i in anomalyType[1].iteritems():
            # print idAnomalyType[0], anomalyType[0], i[0], i[1], format(i[1] * 1.0 / allSixCounter[i[0]], '0.4%'), eachSixDic[anomalyType[0]][i[0]]
            year = patientIdDic[idAnomalyType[0]]
            if year in yearInterventionNum:
                if i[0] in yearInterventionNum[year]:
                    yearInterventionNum[year][i[0]] += i[1]
                else:
                    yearInterventionNum[year][i[0]] = {}
                    yearInterventionNum[year][i[0]] = i[1]
            else:
                yearInterventionNum[year] = {}
                yearInterventionNum[year][i[0]] = i[1]
            if year in yearAnomalyInterventionDict:
                if anomalyType[0] in yearAnomalyInterventionDict[year]:
                    if i[0] in yearAnomalyInterventionDict[year][anomalyType[0]]:
                        yearAnomalyInterventionDict[year][anomalyType[0]][i[0]] += i[1]
                    else:
                        yearAnomalyInterventionDict[year][anomalyType[0]][i[0]] = i[1]
                else:
                    yearAnomalyInterventionDict[year][anomalyType[0]] = {}
                    yearAnomalyInterventionDict[year][anomalyType[0]][i[0]] = i[1]
            else:
                yearAnomalyInterventionDict[year] = {}
                yearAnomalyInterventionDict[year][anomalyType[0]] = {}
                yearAnomalyInterventionDict[year][anomalyType[0]][i[0]] = i[1]
i = 0
j = 0
sheet = workbook.add_sheet("year rate", cell_overwrite_ok=True)

##{"2008":{"LESS":{"单硝酸异山梨酯":3}}}
for yearAnomalyInterventionNum in yearAnomalyInterventionDict.iteritems():
    year = yearAnomalyInterventionNum[0]

    for anomalyInterventionNum in yearAnomalyInterventionNum[1].iteritems():
        for interventionNum in anomalyInterventionNum[1].iteritems():
            anomaly = anomalyInterventionNum[0]
            intervention = interventionNum[0]
            sheet.write(j, 0, year)
            sheet.write(j, 1, anomaly)
            sheet.write(j, 2, intervention)
            sheet.write(j, 3, logyearInterventionNum[year][intervention])
            sheet.write(j, 4, interventionNum[1])
            sheet.write(j, 5, format(interventionNum[1] * 1.0 / logyearInterventionNum[year][intervention], '0.4%'))
            print year, anomaly, intervention, interventionNum[1], logyearInterventionNum[year][intervention], \
                yearInterventionNum[year][intervention], format(
                interventionNum[1] * 1.0 / logyearInterventionNum[year][intervention], '0.4%')
            j += 1
    i += 1
k = 0
usableRateIndex = 0
usableCountIndex = 0
sheet = workbook.add_sheet("year rate can use", cell_overwrite_ok=True)
rateSheet = workbook.add_sheet("year rate can use for graph", cell_overwrite_ok=True)
countSheet = workbook.add_sheet("year count can use for graph", cell_overwrite_ok=True)
isRateUsable = False
isCountUsable = False
isAllYearUsable = True
for i in allSixCounter.iteritems():
    for j in eachSixDic.iteritems():
        anomaly = j[0]
        intervention = i[0]
        isAllYearUsable = True
        for year in { "20081", "20082", "20083", "20090", "20091", "20092", "20093", "20100", "20101", "20102",
                     "20103"}:
            if year not in yearAnomalyInterventionDict or anomaly not in yearAnomalyInterventionDict[year] or intervention not in yearAnomalyInterventionDict[year][anomaly]:
                isAllYearUsable = False
                break

        if isAllYearUsable:
            print "isAllYearUsable"
            for year in {"20081", "20082", "20083", "20090", "20091", "20092", "20093", "20100", "20101",
                         "20102", "20103"}:
                sheet.write(k, 0, year)
                sheet.write(k, 1, anomaly)
                sheet.write(k, 2, intervention)
                sheet.write(k, 3, logyearInterventionNum[year][intervention])
                sheet.write(k, 4, yearAnomalyInterventionDict[year][anomaly][intervention])
                sheet.write(k, 5, format(
                    (yearAnomalyInterventionDict[year][anomaly][intervention]) * 1.0 / logyearInterventionNum[year][
                        intervention], '0.4%'))
                k+=1


                # if intervention in yearAnomalyInterventionDict[2008][anomaly] and intervention in \
                #         yearAnomalyInterventionDict[2009][anomaly] and intervention in yearAnomalyInterventionDict[2010][
                #     anomaly]:
                #     count2008 = yearAnomalyInterventionDict[2008][anomaly][intervention]
                #     count2009 = yearAnomalyInterventionDict[2009][anomaly][intervention]
                #     count2010 = yearAnomalyInterventionDict[2010][anomaly][intervention]
                #     rate2008 = count2008 * 1.0 / logyearInterventionNum[2008][intervention]
                #     rate2009 = count2009 * 1.0 / logyearInterventionNum[2009][intervention]
                #     rate2010 = count2010 * 1.0 / logyearInterventionNum[2010][intervention]
                #     if (rate2009 - rate2008) != 0 and abs((rate2010 - rate2009) / (rate2009 - rate2008) - 1) < 0.2:
                #         isRateUsable = True
                #     if (count2009 - count2008) != 0 and abs((count2010 - count2009) * 1.0 / (count2009 - count2008) - 1) < 0.2:
                #         isCountUsable = True
                #     for year in {2008, 2009, 2010}:
                #         sheet.write(k, 0, year)
                #         sheet.write(k, 1, anomaly)
                #         sheet.write(k, 2, intervention)
                #         sheet.write(k, 3, logyearInterventionNum[year][intervention])
                #         sheet.write(k, 4, yearAnomalyInterventionDict[year][anomaly][intervention])
                #         sheet.write(k, 5, format(
                #             (yearAnomalyInterventionDict[year][anomaly][intervention]) * 1.0 / logyearInterventionNum[year][
                #                 intervention], '0.4%'))
                #         if isRateUsable:
                #             rateSheet.write(usableRateIndex, 0, year)
                #             rateSheet.write(usableRateIndex, 1, anomaly)
                #             rateSheet.write(usableRateIndex, 2, intervention)
                #             rateSheet.write(usableRateIndex, 3, logyearInterventionNum[year][intervention])
                #             rateSheet.write(usableRateIndex, 4, yearAnomalyInterventionDict[year][anomaly][intervention])
                #             rateSheet.write(usableRateIndex, 5, format(
                #                 (yearAnomalyInterventionDict[year][anomaly][intervention]) * 1.0 / logyearInterventionNum[year][
                #                     intervention], '0.4%'))
                #             rateSheet.write(usableRateIndex, 6, (rate2010 - rate2009) / (rate2009 - rate2008))
                #             usableRateIndex += 1
                #         k += 1
                #         if isCountUsable:
                #             countSheet.write(usableCountIndex, 0, year)
                #             countSheet.write(usableCountIndex, 1, anomaly)
                #             countSheet.write(usableCountIndex, 2, intervention)
                #             countSheet.write(usableCountIndex, 3, logyearInterventionNum[year][intervention])
                #             countSheet.write(usableCountIndex, 4, yearAnomalyInterventionDict[year][anomaly][intervention])
                #             countSheet.write(usableCountIndex, 5, format(
                #                 (yearAnomalyInterventionDict[year][anomaly][intervention]) * 1.0 / logyearInterventionNum[year][
                #                     intervention], '0.4%'))
                #             countSheet.write(usableCountIndex, 6, (count2010 - count2009) * 1.0 / (count2009 - count2008))
                #             usableCountIndex += 1
                #     isRateUsable = False
                #     isCountUsable = False

workbook.save('test2.xls')
# for i in yearInterventionNum.iteritems():
#     for j in i[1].iteritems():
#         print i[0], j[0], j[1]
# for i in eachSixDic.iteritems():
#     for j in i[1].iteritems():
#         print i[0], j[0], j[1], allSixCounter[j[0]], format(j[1] * 1.0 / allSixCounter[j[0]], '0.4%'),j[1], format(j[1] * 1.0 / normalizedNameCounters.get(j[0], -1), '0.4%')
