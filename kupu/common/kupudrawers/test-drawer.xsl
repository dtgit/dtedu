<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output indent="yes"/>
    <xsl:strip-space elements="libraries library items resource collection"/>
    <xsl:param name="selectid">buttons.png</xsl:param>
    <xsl:template match="/libraries">
        <xsl:processing-instruction name="oxygen">
            RNGSchema="file:libraries.rng"
            type="xml"
        </xsl:processing-instruction>
        <xsl:processing-instruction name="xml-stylesheet">href="drawer.xsl"</xsl:processing-instruction>
        <xsl:copy>
            <param name="drawertype">link</param>
            <param name="drawertitle">Test Link Drawer</param>
            <param name="showupload">yes</param>
            <param name="usecaptions">yes</param>
                <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="*">
        <xsl:copy>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="text()|@*">
        <xsl:value-of select="."/>
    </xsl:template>
    <xsl:template match="status">
        <status>
        <xsl:attribute name="class"><xsl:value-of select="@class"/></xsl:attribute>
        <xsl:apply-templates/>
        </status>
    </xsl:template>
    <xsl:template match="*[@id]">
        <xsl:copy>
            <xsl:attribute name="id">
                <xsl:value-of select="@id"/>
            </xsl:attribute>
            <xsl:choose>
                <xsl:when test="@id='allimages'">
                    <xsl:attribute name="selected">selected</xsl:attribute>
                    <xsl:apply-templates select="uri|title|icon"/>
                    <xsl:copy-of select="document(concat('../',src))/collection/breadcrumbs"/>
                    <xsl:apply-templates select="document(concat('../',src))/collection/items"/>
                </xsl:when>
                <xsl:when test="@id='kupubuttons'">
                    <xsl:attribute name="selected">selected</xsl:attribute>
                    <xsl:apply-templates select="uri|title|icon"/>
                        <xsl:apply-templates select="document(concat('../',src))/collection/items"/>
                </xsl:when>
                <xsl:when test="@id='collection-allimages.xml'">
                    <xsl:attribute name="selected">selected</xsl:attribute>
                    <xsl:apply-templates/>
                </xsl:when>
                <xsl:when test="@id=$selectid">
                    <xsl:attribute name="selected">selected</xsl:attribute>
                    <xsl:apply-templates/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:apply-templates/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>
