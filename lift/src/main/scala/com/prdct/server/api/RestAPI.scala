package com.prdct.server.api

import xml.{Elem, NodeSeq}

import net.liftweb.http._;
import net.liftweb.http.rest.XMLApiHelper 

import com.prdct.server.api.RestFormatters._
import com.prdct.server.model.User

import org.slf4j.LoggerFactory

object DispatchRestAPI extends XMLApiHelper {
  //private val log = LoggerFactory.getLogger(this.getClass)

  def dispatch: LiftRules.DispatchPF = {
    case Req(List("api", "users"), _, GetRequest) => 
      () => nodeSeqToResponse(toXml(getAllUsers)) 
    case Req(List("api", "users"), "xml", GetRequest) => 
      () => nodeSeqToResponse(toXml(getAllUsers)) 
    case Req(List("api", "users"), "json", GetRequest) => 
      () => JsonResponse(toJSON(getAllUsers))
    case Req("api" :: x :: Nil, "", _) => 
      () => BadResponse() // Everything else fails 
  }

  def getAllUsers = {
    //log.info("GET ALL USERS")
    new User
  }

  def createTag(nodeSeq: NodeSeq): Elem = {
    <xml>
      {nodeSeq}
    </xml>
  }
}
