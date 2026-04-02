import discord


class ParsingService:
  def __init__(self, valid_numbers, valid_letters, valid_symbols, string)
  valid_numbers = [1,2,3,4,5,6,7,8,9,0]
  valid_letters = [A,a,B,b,C,c,D,d,E,e,F,f,G,g,H,h,I,i,J,j,K,k,L,l,M,m,N,n,O,o,P,p,Q,q,R,r,S,s,T,t,U,u,V,v,W,w,X,x,Y,y,Z,z] # Put In Quotes
  valid_operators = [+,-,/,*,(,)
  self.valid_numbers = valid_numbers
  self.valid_letters  = valid_letters
  self.valid_symbols = valid_symbols,
  self.string = string
  self.valid_operators = valid_operators



# turn all these to async I think
def check_for_numbers(string)
 return if any(valid_numbers) in string or typeof(string) == int or tyoeof(string) == float
def check_has_operators(string)
  return if any(self.valid_operators) in self.string 
def check_valid_math(string)
  if check_for_numbers(string) and check_has_operators(string):
    if pass # if the string has the pattern of NUMBER OPERRATOR NUMBER and DOES NOT have an OPERATOR at the END without 
            # another number next to the operator, so if the last character of the string is a operator or the very first 
            # character of the string is an operator (should I mention this is the math part) then we ignoe the first character and only error
            # if something else is wrong
            # in this case we should ignore the last character as long as the rest of the string  is valid

  if pass # STRING contains an open paranthesis and not a closed one or vice vers.
          # then we say its invalid and if we are able to we ignore it if its the last step, otherwise we
          # escalate this
          # if the string has invalid paranthesess at all then we do the proper action\
  
